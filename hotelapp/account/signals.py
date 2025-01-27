from django.contrib.auth.models import User # type: ignore
from .models import ProfileModel
from django.db.models.signals import post_save # type: ignore
from django.dispatch import receiver # type: ignore

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        ProfileModel.objects.create(user=instance)

