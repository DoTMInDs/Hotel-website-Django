from django.db.models.signals import post_save # type: ignore
from django.dispatch import receiver # type: ignore
from .models import ProfileModel
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    from .models import ProfileModel   # avoid circular import
    if created:
        ProfileModel.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profilemodel"):
        instance.profilemodel.save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_guest_profile(sender, instance, created, **kwargs):
    """Automatically create a Guest profile when a new user registers"""
    from core.models import Guest  # avoid circular import
    if created and instance.user_type == 'Guest':
        Guest.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name or '',
                'last_name': instance.last_name or '',
                'email': instance.email or '',
            }
        )

