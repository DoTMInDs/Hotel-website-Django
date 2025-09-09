from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_welcome_email(user):
    """
    Send welcome email to newly registered users
    """
    domain = getattr(settings, 'DOMAIN', None)
    if not domain:
        domain = 'baselink.onrender.com'
    subject = 'Welcome to BaseLink - Your Account Has Been Created!'
    
    # HTML version of the email
    html_message = render_to_string('core/emails/welcome_email.html', {
        'user': user,
        'domain': domain,
        'site_name': getattr(settings, 'SITE_NAME', 'BaseLink')
    })
    
    # Plain text version
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'essetech@zohomail.com'),
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False