"""
accounts/tasks.py — transactional email for auth flows.

Runs outside the request cycle (eager in dev, queued in prod) so the API
responds immediately and email failures never block authentication.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, *, email: str, reset_url: str) -> None:
    try:
        send_mail(
            subject='Reset your Sanad password',
            message=(
                'We received a request to reset your Sanad password.\n\n'
                f'Reset it here: {reset_url}\n\n'
                'This link expires in 1 hour. If you did not request this, '
                'you can safely ignore this email.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error('Failed to send password-reset email to %s: %s', email, exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_verification(self, *, email: str, verify_url: str) -> None:
    try:
        send_mail(
            subject='Verify your Sanad email',
            message=(
                'Welcome to Sanad.\n\n'
                f'Please confirm your email address: {verify_url}\n\n'
                'This link expires in 3 days.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error('Failed to send verification email to %s: %s', email, exc)
        raise self.retry(exc=exc)
