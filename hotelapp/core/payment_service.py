import hashlib
import hmac
import json
import logging
import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Booking, Reservation

logger = logging.getLogger(__name__)


class PaystackPaymentService:
    """Service class to handle Paystack payment operations with subaccount support for hotel payments"""
    
    BASE_URL = "https://api.paystack.co"
    
    @staticmethod
    def verify_webhook_signature(request_body, signature):
        """Verify webhook signature from Paystack"""
        if not signature:
            return False
        
        secret_key = settings.PAYSTACK_SECRET_KEY
        if not secret_key:
            raise ValidationError("Paystack secret key not configured")
        
        # Paystack uses HMAC-SHA512
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            request_body,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    @staticmethod
    def initialize_payment(email, amount, reference, callback_url, 
                          metadata=None, hotel_subaccount=None, currency="GHS"):
        """Initialize payment with Paystack and support subaccount split payments"""
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        # Convert amount to kobo (smallest currency unit)
        amount_in_kobo = int(float(amount) * 100)
        
        data = {
            "email": email,
            "amount": amount_in_kobo,
            "currency": currency,
            "reference": reference,
            "callback_url": callback_url,
            "metadata": metadata or {}
        }
        
        # Add subaccount for hotel if provided (for split payments)
        if hotel_subaccount:
            data["subaccount"] = hotel_subaccount
            data["bearer"] = "subaccount"  # Who bears the transaction charges
        
        try:
            response = requests.post(
                f"{PaystackPaymentService.BASE_URL}/transaction/initialize",
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("status"):
                return {
                    "status": True,
                    "data": {
                        "authorization_url": result["data"]["authorization_url"],
                        "access_code": result["data"]["access_code"],
                        "reference": result["data"]["reference"]
                    }
                }
            else:
                return {
                    "status": False,
                    "message": result.get("message", "Payment initialization failed")
                }
        except requests.RequestException as e:
            logger.error(f"Paystack payment initialization error: {str(e)}")
            raise ValidationError(f"Payment initialization failed: {str(e)}")
    
    @staticmethod
    def verify_payment(reference):
        """Verify payment with Paystack using reference"""
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.get(
                f"{PaystackPaymentService.BASE_URL}/transaction/verify/{reference}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("status"):
                return {
                    "status": True,
                    "data": result["data"]
                }
            else:
                return {
                    "status": False,
                    "message": result.get("message", "Payment verification failed")
                }
        except requests.RequestException as e:
            logger.error(f"Paystack payment verification error: {str(e)}")
            raise ValidationError(f"Payment verification failed: {str(e)}")
    
    @staticmethod
    def create_subaccount(business_name, settlement_bank, account_number, 
                         percentage_charge, primary_contact_email, 
                         primary_contact_name, primary_contact_phone):
        """Create a subaccount for a hotel to receive split payments"""
        headers = {
            "Authorization": f"Bearer {settings.PAYTSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        data = {
            "business_name": business_name,
            "settlement_bank": settlement_bank,
            "account_number": account_number,
            "percentage_charge": percentage_charge,
            "primary_contact_email": primary_contact_email,
            "primary_contact_name": primary_contact_name,
            "primary_contact_phone": primary_contact_phone
        }
        
        try:
            response = requests.post(
                f"{PaystackPaymentService.BASE_URL}/subaccount",
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("status"):
                return {
                    "status": True,
                    "data": result["data"]
                }
            else:
                return {
                    "status": False,
                    "message": result.get("message", "Subaccount creation failed")
                }
        except requests.RequestException as e:
            logger.error(f"Paystack subaccount creation error: {str(e)}")
            raise ValidationError(f"Subaccount creation failed: {str(e)}")


@csrf_exempt
@require_http_methods(["POST"])
def paystack_webhook(request):
    """Handle Paystack webhook for payment notifications"""
    try:
        signature = request.headers.get('x-paystack-signature')
        if not signature:
            logger.warning("Paystack webhook received without signature")
            return HttpResponse(status=400)
        
        if not PaystackPaymentService.verify_webhook_signature(request.body, signature):
            logger.warning("Paystack webhook signature verification failed")
            return HttpResponse(status=400)
        
        webhook_data = json.loads(request.body)
        event = webhook_data.get("event")
        data = webhook_data.get("data", {})
        
        if event == "charge.success":
            reference = data.get("reference")
            status = data.get("status")
            
            if status == "success" and reference:
                try:
                    booking = Booking.objects.get(paystack_reference=reference)
                    if not booking.is_paid:
                        booking.is_paid = True
                        booking.save()
                        
                        # Create reservation from booking
                        try:
                            reservation = Reservation.create_from_booking(booking)
                            logger.info(f"Reservation {reservation.id} created from booking {booking.id}")
                        except Exception as e:
                            logger.error(f"Failed to create reservation from booking: {str(e)}")
                        
                        # Send booking confirmation email
                        subject = "Booking Confirmation - Payment Successful"
                        message = render_to_string("emails/booking_confirmation.html", {
                            'booking': booking,
                            'guest': booking.guest,
                        })
                        
                        send_mail(
                            subject,
                            '',
                            settings.DEFAULT_FROM_EMAIL,
                            [booking.guest.email],
                            html_message=message,
                            fail_silently=True
                        )
                        
                        logger.info(f"Booking {booking.id} marked as paid via Paystack webhook. Reference: {reference}")
                        
                except Booking.DoesNotExist:
                    logger.warning(f"Booking not found for reference: {reference}")
                    pass
        
        return HttpResponse(status=200)
        
    except (json.JSONDecodeError, KeyError, ValidationError) as e:
        logger.error(f"Paystack webhook parsing error: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Paystack webhook processing error: {str(e)}")
        return HttpResponse(status=500)


# For backward compatibility
PaymentService = PaystackPaymentService