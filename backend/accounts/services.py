"""
accounts/services.py — authentication and user management business logic.

Rules:
  - No HTTP objects (request/response) here.
  - No DRF serializers here.
  - Raise ValueError / RuntimeError on business rule violations.
"""
import logging
import uuid

import requests as http_requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.db import IntegrityError
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.text import slugify
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile

_EMAIL_VERIFY_SALT = 'sanad.email-verify'
_EMAIL_VERIFY_MAX_AGE = 60 * 60 * 24 * 3  # 3 days

_GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'

try:
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests
    _GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    _GOOGLE_AUTH_AVAILABLE = False

logger = logging.getLogger(__name__)
User = get_user_model()


# ── Token helpers ─────────────────────────────────────────────────────────────

def issue_tokens(user: User) -> dict:
    """Return a new JWT access + refresh pair for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def blacklist_token(refresh_token_str: str) -> None:
    """Blacklist a refresh token. Raises ValueError on invalid token."""
    try:
        token = RefreshToken(refresh_token_str)
        token.blacklist()
    except TokenError as exc:
        raise ValueError(str(exc)) from exc


# ── Registration & login ──────────────────────────────────────────────────────

def register(*, username: str, email: str, password: str) -> User:
    """
    Create a new regular user account.
    The post_save signal (accounts/signals.py) creates a UserProfile automatically.
    """
    email = email.lower()
    user = User.objects.create_user(username=username, email=email, password=password)
    try:
        send_verification_email(user)
    except Exception:
        logger.exception('Failed to dispatch verification email for %s', email)
    return user


def authenticate(*, email: str, password: str) -> User:
    """
    Verify email + password credentials.
    Raises ValueError with a safe message on any failure.
    """
    email = email.lower()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValueError('Invalid credentials.')

    if not user.check_password(password):
        raise ValueError('Invalid credentials.')

    if not user.is_active:
        raise ValueError('Account is inactive.')

    return user


# ── Google Sign-In: shared user resolution ───────────────────────────────────

def _provision_google_user(idinfo: dict, email: str) -> User:
    """
    Create a brand-new user for a first-time Google sign-in.

    Username is a friendly, readable handle derived from the Google profile
    name (e.g. "Ahmed Bashir" → "ahmed-bashir"), so SSO users never surface as
    an opaque "google_…" slug in author/comment bylines. When no usable name is
    present it falls back to a random opaque slug.

    Creation is collision-safe: a clash on the unique username retries with a
    fresh suffix; a clash on the unique email (a rare concurrent first-time
    login for the same address) returns the account that won the race.
    """
    first = idinfo.get('given_name', '')
    last = idinfo.get('family_name', '')
    # allow_unicode keeps Arabic names intact (e.g. "أحمد بشير" → "أحمد-بشير").
    base = slugify(f'{first} {last}'.strip(), allow_unicode=True)

    for attempt in range(6):
        if base:
            username = base if attempt == 0 else f'{base}-{uuid.uuid4().hex[:6]}'
        else:
            username = f'google_{uuid.uuid4().hex[:20]}'
        try:
            return User.objects.create_user(
                username=username, email=email,
                first_name=first, last_name=last,
            )
        except IntegrityError:
            # Email is unique too: if it now exists, another request created the
            # account concurrently — adopt it. Otherwise the clash was on the
            # username, so loop and retry with a fresh suffix.
            existing = User.objects.filter(email=email).first()
            if existing is not None:
                return existing

    # Friendly handles exhausted (astronomically unlikely) — opaque, full-length
    # UUID slug is collision-proof for all practical purposes.
    return User.objects.create_user(
        username=f'google_{uuid.uuid4().hex}', email=email,
        first_name=first, last_name=last,
    )


def _resolve_google_user(idinfo: dict) -> User:
    """
    Given a verified Google ID token payload, look up or create the Django user.

    Steps:
      1. Look up UserProfile by stable google_uid (survives email changes).
      2. Fall back to email lookup for first-time Google sign-in.
      3. Create account if email is unknown.
      4. Link google_uid to the profile and mark email verified.

    Raises ValueError if the account is inactive.
    """
    if not idinfo.get('email_verified', False):
        raise ValueError('Google account email is not verified.')

    email = idinfo.get('email', '').lower()
    if not email:
        raise ValueError('Google account has no email address.')

    google_uid: str = idinfo['sub']

    # Step 1: stable UID lookup
    user = None
    try:
        profile = UserProfile.objects.select_related('user').get(google_uid=google_uid)
        user = profile.user
        if user.email != email:
            user.email = email
            user.save(update_fields=['email'])
    except UserProfile.DoesNotExist:
        pass

    # Step 2-3: email lookup / account creation
    if user is None:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = _provision_google_user(idinfo, email)

    # Step 4: link google_uid + mark verified
    profile = user.profile
    update_fields = []
    if not profile.google_uid:
        profile.google_uid = google_uid
        update_fields.append('google_uid')
    if not profile.is_email_verified:
        profile.is_email_verified = True
        update_fields.append('is_email_verified')
    if update_fields:
        profile.save(update_fields=update_fields)

    if not user.is_active:
        raise ValueError('Account is inactive.')

    return user


def google_sign_in(*, id_token_str: str) -> User:
    """
    Verify a Google ID token (GSI popup flow) and return the matching User.

    Raises:
      RuntimeError: if google-auth package is missing or GOOGLE_CLIENT_ID unset.
      ValueError: if the token is invalid or the account is inactive.
    """
    if not _GOOGLE_AUTH_AVAILABLE:
        raise RuntimeError('google-auth package is not installed.')

    if not settings.GOOGLE_CLIENT_ID:
        raise RuntimeError('GOOGLE_CLIENT_ID is not configured.')

    try:
        idinfo = google_id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        logger.warning('Google ID token verification failed', exc_info=True)
        raise ValueError('Invalid Google token.')

    return _resolve_google_user(idinfo)


def google_oauth_exchange(*, code: str, redirect_uri: str, code_verifier: str) -> User:
    """
    OAuth2 Authorization Code + PKCE flow.

    Exchange the authorization code for tokens, verify the ID token,
    and return (or create) the matching Django user.

    The redirect_uri MUST exactly match the value registered in Google Cloud
    Console AND the value used when building the authorization URL.

    Raises:
      RuntimeError: if google-auth or configuration is missing.
      ValueError: on token exchange failure, invalid token, or inactive account.
    """
    if not _GOOGLE_AUTH_AVAILABLE:
        raise RuntimeError('google-auth package is not installed.')

    if not settings.GOOGLE_CLIENT_ID:
        raise RuntimeError('GOOGLE_CLIENT_ID is not configured.')

    if not settings.GOOGLE_CLIENT_SECRET:
        raise RuntimeError('GOOGLE_CLIENT_SECRET is not configured.')

    # Exchange authorization code → token response
    try:
        token_response = http_requests.post(
            _GOOGLE_TOKEN_URL,
            data={
                'code': code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
                'code_verifier': code_verifier,
            },
            timeout=10,
        )
        token_response.raise_for_status()
    except http_requests.exceptions.Timeout:
        logger.error('Google token exchange timed out')
        raise RuntimeError('Google authentication service timed out. Please try again.')
    except http_requests.exceptions.HTTPError as exc:
        logger.warning('Google token exchange HTTP error: %s', exc.response.text)
        raise ValueError('Authorization code is invalid or has already been used.')
    except http_requests.exceptions.RequestException as exc:
        logger.error('Google token exchange network error: %s', exc)
        raise RuntimeError('Could not reach Google authentication service.')

    token_data = token_response.json()
    id_token_str = token_data.get('id_token')
    if not id_token_str:
        logger.warning('Google token exchange returned no id_token: %s', token_data)
        raise ValueError('Google did not return an ID token.')

    # Verify the ID token's signature, iss, aud, and exp
    try:
        idinfo = google_id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        logger.warning('Google ID token verification failed after code exchange', exc_info=True)
        raise ValueError('Google token verification failed.')

    return _resolve_google_user(idinfo)


# ── Password reset ────────────────────────────────────────────────────────────

def request_password_reset(*, email: str) -> None:
    """
    Dispatch a password-reset email if the account exists.
    Always returns None — never reveals whether the email is registered.
    """
    email = email.lower().strip()
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        logger.info('Password reset requested for unknown email — ignoring.')
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'

    from .tasks import send_password_reset_email
    send_password_reset_email.delay(email=user.email, reset_url=reset_url)


def confirm_password_reset(*, uid: str, token: str, new_password: str) -> None:
    """
    Validate a reset token and set the new password.
    Raises ValueError on any invalid/expired input.
    """
    try:
        user_pk = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_pk)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise ValueError('Invalid or expired reset link.')

    if not default_token_generator.check_token(user, token):
        raise ValueError('Invalid or expired reset link.')

    user.set_password(new_password)
    user.save(update_fields=['password'])


# ── Email verification ────────────────────────────────────────────────────────

def send_verification_email(user: User) -> None:
    """Dispatch a signed email-verification link."""
    token = signing.dumps({'uid': user.pk}, salt=_EMAIL_VERIFY_SALT)
    verify_url = f'{settings.FRONTEND_URL}/verify-email?token={token}'
    from .tasks import send_email_verification
    send_email_verification.delay(email=user.email, verify_url=verify_url)


def confirm_email_verification(*, token: str) -> User:
    """Validate a signed verification token and mark the profile verified."""
    try:
        payload = signing.loads(token, salt=_EMAIL_VERIFY_SALT, max_age=_EMAIL_VERIFY_MAX_AGE)
    except signing.SignatureExpired:
        raise ValueError('Verification link has expired.')
    except signing.BadSignature:
        raise ValueError('Invalid verification link.')

    try:
        user = User.objects.select_related('profile').get(pk=payload['uid'])
    except (KeyError, User.DoesNotExist):
        raise ValueError('Invalid verification link.')

    profile = user.profile
    if not profile.is_email_verified:
        profile.is_email_verified = True
        profile.save(update_fields=['is_email_verified'])
    return user
