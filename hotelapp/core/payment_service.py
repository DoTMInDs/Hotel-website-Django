import hashlib
import hmac
import json
import requests
import logging
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Booking

logger = logging.getLogger(__name__)


class HubtelPaymentService:
    """Service class to handle HUBTEL payment operations securely with split payments"""
    
    BASE_URL = "https://api.hubtel.com/v1"
    
    @staticmethod
    def verify_webhook_signature(request_body, signature):
        """Verify webhook signature from HUBTEL"""
        if not signature:
            return False
        
        secret_key = settings.HUBTEL_SECRET_KEY
        if not secret_key:
            raise ValidationError("HUBTEL secret key not configured")
        
        # HUBTEL uses HMAC-SHA256
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    @staticmethod
    def initialize_payment(email, amount, reference, callback_url, customer_name="", phone="", hotel_momo=""):
        """Initialize payment with HUBTEL and setup split payment"""
        headers = {
            "Authorization": f"Bearer {settings.HUBTEL_API_KEY}",
            "Content-Type": "application/json",
        }
        
        # Build split payment recipients if hotel MoMo is provided
        recipients = []
        if hotel_momo:
            recipients.append({
                "accountNumber": hotel_momo,
                "accountType": "momo",  # "momo", "bank", or "wallet"
                "amount": float(amount),
                "description": "Hotel payment"
            })
        
        data = {
            "amount": float(amount),
            "currency": settings.HUBTEL_CURRENCY,
            "description": f"Hotel booking payment - Reference: {reference}",
            "reference": reference,
            "returnUrl": callback_url,
            "cancelUrl": callback_url,
            "customer": {
                "email": email,
                "name": customer_name,
                "phone": phone
            }
        }
        
        # Add recipients if any
        if recipients:
            data["recipients"] = recipients
        
        try:
            response = requests.post(
                f"{HubtelPaymentService.BASE_URL}/transactions/init",
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "success" or result.get("responseCode") == "0000":
                checkout_url = result.get("data", {}).get("checkoutUrl") or result.get("checkoutUrl")
                if not checkout_url:
                    checkout_url = result.get("data", {}).get("link")
                
                return {
                    "status": True,
                    "data": {
                        "link": checkout_url,
                    }
                }
            else:
                return {
                    "status": False,
                    "message": result.get("message", "Payment initialization failed")
                }
        except requests.RequestException as e:
            logger.error(f"HUBTEL payment initialization error: {str(e)}")
            raise ValidationError(f"Payment initialization failed: {str(e)}")
    
    @staticmethod
    def verify_payment(reference):
        """Verify payment with HUBTEL using reference"""
        headers = {
            "Authorization": f"Bearer {settings.HUBTEL_API_KEY}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.get(
                f"{HubtelPaymentService.BASE_URL}/transactions/{reference}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"HUBTEL payment verification error: {str(e)}")
            raise ValidationError(f"Payment verification failed: {str(e)}")


@csrf_exempt
@require_http_methods(["POST"])
def hubtel_webhook(request):
    """Handle HUBTEL webhook securely with split payment confirmation"""
    try:
        signature = request.headers.get('X-Hubtel-Signature')
        if not signature:
            logger.warning("HUBTEL webhook received without signature")
            return HttpResponse(status=400)
        
        if not HubtelPaymentService.verify_webhook_signature(request.body, signature):
            logger.warning("HUBTEL webhook signature verification failed")
            return HttpResponse(status=400)
        
        webhook_data = json.loads(request.body)
        event_type = webhook_data.get("event")
        data = webhook_data.get("data", {})
        
        if event_type == "transaction.completed":
            status = data.get("status")
            if status == "completed" or status == "success":
                reference = data.get("reference")
                transaction_id = data.get("transactionId")
                
                if reference:
                    try:
                        booking = Booking.objects.get(hubtel_reference=reference)
                        if not booking.is_paid:
                            booking.is_paid = True
                            booking.save()
                            
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
                            
                            logger.info(f"Booking {booking.id} marked as paid via HUBTEL webhook. Transaction ID: {transaction_id}. Split payment processed.")
                            
                    except Booking.DoesNotExist:
                        logger.warning(f"Booking not found for reference: {reference}")
                        pass
        
        return HttpResponse(status=200)
        
    except (json.JSONDecodeError, KeyError, ValidationError) as e:
        logger.error(f"HUBTEL webhook parsing error: {str(e)}")
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"HUBTEL webhook processing error: {str(e)}")
        return HttpResponse(status=500)


# For backward compatibility
PaymentService = HubtelPaymentService 