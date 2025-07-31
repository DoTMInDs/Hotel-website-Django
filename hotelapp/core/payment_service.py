import hashlib
import hmac
import json
import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Booking


class PaymentService:
    """Service class to handle Paystack payment operations securely"""
    
    @staticmethod
    def verify_webhook_signature(request_body, signature):
        """Verify webhook signature from Paystack"""
        if not signature:
            return False
        
        # Get the secret key
        secret_key = settings.PAYSTACK_SECRET_KEY
        if not secret_key:
            raise ValidationError("Paystack secret key not configured")
        
        # Create HMAC hash
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            request_body,
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    @staticmethod
    def initialize_payment(email, amount, reference, callback_url):
        """Initialize payment with Paystack"""
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
        data = {
            "email": email,
            "amount": int(amount * 100),  # Convert to kobo
            "reference": reference,
            "callback_url": callback_url
        }
        
        try:
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValidationError(f"Payment initialization failed: {str(e)}")
    
    @staticmethod
    def verify_payment(reference):
        """Verify payment with Paystack"""
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }
        
        try:
            response = requests.get(
                f"https://api.paystack.co/transaction/verify/{reference}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValidationError(f"Payment verification failed: {str(e)}")


@csrf_exempt
@require_http_methods(["POST"])
def paystack_webhook(request):
    """Handle Paystack webhook securely"""
    try:
        # Get the webhook signature
        signature = request.headers.get('X-Paystack-Signature')
        if not signature:
            return HttpResponse(status=400)
        
        # Verify the signature
        if not PaymentService.verify_webhook_signature(request.body, signature):
            return HttpResponse(status=400)
        
        # Parse the webhook data
        webhook_data = json.loads(request.body)
        event = webhook_data.get('event')
        data = webhook_data.get('data', {})
        
        if event == 'charge.success':
            reference = data.get('reference')
            if reference:
                try:
                    booking = Booking.objects.get(paystack_reference=reference)
                    if not booking.is_paid:
                        booking.is_paid = True
                        booking.save()
                        
                        # Send confirmation email
                        from django.core.mail import send_mail
                        from django.template.loader import render_to_string
                        
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
                        
                except Booking.DoesNotExist:
                    pass  # Booking not found, ignore
        
        return HttpResponse(status=200)
        
    except (json.JSONDecodeError, KeyError, ValidationError) as e:
        return HttpResponse(status=400)
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Webhook processing error: {str(e)}")
        return HttpResponse(status=500) 