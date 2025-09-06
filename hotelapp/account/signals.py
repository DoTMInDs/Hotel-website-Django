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

