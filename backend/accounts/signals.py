from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    """
    Guarantee every User always has a UserProfile — regardless of how
    the user was created (API, admin, management command, tests, migrations).

    Using get_or_create instead of create so the signal is safe to fire
    multiple times (e.g. if save() is called more than once on a new user).
    """
    if created:
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=instance)
