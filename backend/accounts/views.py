import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from base.responses import success, created
from . import services as auth_services
from .serializers import RegisterSerializer, UserSerializer, MeUpdateSerializer

logger = logging.getLogger(__name__)

_COOKIE = settings.AUTH_COOKIE_NAME


# ── Cookie helpers ────────────────────────────────────────────────────────────

def _set_refresh_cookie(response: Response, refresh_token_str: str) -> None:
    """Attach the refresh token as an HttpOnly cookie to the response."""
    response.set_cookie(
        key=_COOKIE,
        value=refresh_token_str,
        max_age=settings.AUTH_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Remove the refresh token cookie."""
    response.delete_cookie(
        key=_COOKIE,
        path=settings.AUTH_COOKIE_PATH,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )


# ── Throttle ──────────────────────────────────────────────────────────────────

class AuthThrottle(AnonRateThrottle):
    scope = 'auth'


# ── Registration & login ──────────────────────────────────────────────────────

@extend_schema(tags=['auth'])
class RegisterView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AuthThrottle,)

    @extend_schema(
        summary='Register a new user account',
        request=RegisterSerializer,
        responses={201: UserSerializer},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = auth_services.register(**serializer.validated_data)
        tokens = auth_services.issue_tokens(user)
        response = Response(
            {'success': True, 'data': {'user': UserSerializer(user, context={'request': request}).data, 'access': tokens['access']}},
            status=status.HTTP_201_CREATED,
        )
        _set_refresh_cookie(response, tokens['refresh'])
        return response


@extend_schema(tags=['auth'])
class LoginView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AuthThrottle,)

    @extend_schema(
        summary='Log in with email and password',
        responses={200: UserSerializer},
    )
    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        if not email or not password:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Email and password are required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = auth_services.authenticate(email=email, password=password)
        except ValueError as exc:
            return Response(
                {'success': False, 'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        tokens = auth_services.issue_tokens(user)
        response = success({'user': UserSerializer(user, context={'request': request}).data, 'access': tokens['access']})
        _set_refresh_cookie(response, tokens['refresh'])
        return response


@extend_schema(tags=['auth'])
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary='Log out — blacklists the refresh token')
    def post(self, request):
        # Accept refresh token from request body OR from the HttpOnly cookie.
        refresh_token = request.data.get('refresh') or request.COOKIES.get(_COOKIE)
        if not refresh_token:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Refresh token is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            auth_services.blacklist_token(refresh_token)
        except ValueError as exc:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(exc)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = success({'detail': 'Logged out.'}, status_code=status.HTTP_205_RESET_CONTENT)
        _clear_refresh_cookie(response)
        return response


# ── Token refresh from cookie ─────────────────────────────────────────────────

@extend_schema(tags=['auth'])
class CookieTokenRefreshView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary='Silently refresh the access token using the HttpOnly refresh cookie',
        responses={200: None},
    )
    def post(self, request):
        refresh_token_str = request.COOKIES.get(_COOKIE)
        if not refresh_token_str:
            return Response(
                {'success': False, 'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': 'No refresh token cookie.'}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            refresh = RefreshToken(refresh_token_str)
            new_access = str(refresh.access_token)
            # ROTATE_REFRESH_TOKENS=True generates a new refresh token on each use.
            new_refresh = str(refresh)
        except TokenError as exc:
            response = Response(
                {'success': False, 'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            _clear_refresh_cookie(response)
            return response

        response = success({'access': new_access})
        _set_refresh_cookie(response, new_refresh)
        return response


# ── Google SSO: ID token (GSI popup — kept for backward compat) ───────────────

@extend_schema(tags=['auth'])
class GoogleAuthView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AuthThrottle,)

    @extend_schema(
        summary='Sign in or register with a Google ID token (GSI popup flow)',
        responses={200: UserSerializer},
    )
    def post(self, request):
        id_token_str = request.data.get('id_token', '').strip()
        if not id_token_str:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'id_token is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = auth_services.google_sign_in(id_token_str=id_token_str)
        except RuntimeError as exc:
            return Response(
                {'success': False, 'error': {'code': 'SERVER_ERROR', 'message': str(exc)}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ValueError as exc:
            return Response(
                {'success': False, 'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        tokens = auth_services.issue_tokens(user)
        response = success({'user': UserSerializer(user, context={'request': request}).data, 'access': tokens['access']})
        _set_refresh_cookie(response, tokens['refresh'])
        return response


# ── Google SSO: OAuth2 Authorization Code + PKCE ─────────────────────────────

@extend_schema(tags=['auth'])
class GoogleOAuthCallbackView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AuthThrottle,)

    @extend_schema(
        summary='Exchange a Google authorization code for a session (OAuth2 PKCE flow)',
        responses={200: UserSerializer},
    )
    def post(self, request):
        code = request.data.get('code', '').strip()
        redirect_uri = request.data.get('redirect_uri', '').strip()
        code_verifier = request.data.get('code_verifier', '').strip()

        if not code or not redirect_uri or not code_verifier:
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'code, redirect_uri, and code_verifier are all required.',
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = auth_services.google_oauth_exchange(
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier,
            )
        except RuntimeError as exc:
            logger.error('Google OAuth exchange RuntimeError: %s', exc)
            return Response(
                {'success': False, 'error': {'code': 'SERVER_ERROR', 'message': str(exc)}},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except ValueError as exc:
            return Response(
                {'success': False, 'error': {'code': 'AUTHENTICATION_REQUIRED', 'message': str(exc)}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tokens = auth_services.issue_tokens(user)
        response = success({'user': UserSerializer(user, context={'request': request}).data, 'access': tokens['access']})
        _set_refresh_cookie(response, tokens['refresh'])
        return response


# ── Me ────────────────────────────────────────────────────────────────────────

@extend_schema(tags=['auth'])
class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary='Get the authenticated user profile', responses={200: UserSerializer})
    def get(self, request):
        return success(UserSerializer(request.user, context={'request': request}).data)

    @extend_schema(summary='Update the authenticated user profile', request=MeUpdateSerializer, responses={200: UserSerializer})
    def patch(self, request):
        serializer = MeUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Re-fetch so the response reflects the just-saved profile — request.user
        # still holds the pre-update cached profile relation, which would echo
        # stale (e.g. null avatar) data back to the client.
        user = type(request.user).objects.select_related('profile').get(pk=request.user.pk)
        return success(UserSerializer(user, context={'request': request}).data)


# ── Password reset ────────────────────────────────────────────────────────────

@extend_schema(tags=['auth'])
class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AuthThrottle,)

    @extend_schema(summary='Request a password-reset email')
    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Email is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        auth_services.request_password_reset(email=email)
        return success({'detail': 'If an account exists for that email, a reset link has been sent.'})


@extend_schema(tags=['auth'])
class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AuthThrottle,)

    @extend_schema(summary='Set a new password using a reset token')
    def post(self, request):
        uid = request.data.get('uid', '')
        token = request.data.get('token', '')
        new_password = request.data.get('new_password', '')
        if not uid or not token or not new_password:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'uid, token and new_password are required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(new_password) < 8:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'Password must be at least 8 characters.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            auth_services.confirm_password_reset(uid=uid, token=token, new_password=new_password)
        except ValueError as exc:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(exc)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return success({'detail': 'Password has been reset. You can now sign in.'})


# ── Email verification ────────────────────────────────────────────────────────

@extend_schema(tags=['auth'])
class EmailVerifyConfirmView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (AuthThrottle,)

    @extend_schema(summary='Confirm an email address using a verification token')
    def post(self, request):
        token = request.data.get('token', '')
        if not token:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': 'token is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            auth_services.confirm_email_verification(token=token)
        except ValueError as exc:
            return Response(
                {'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': str(exc)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return success({'detail': 'Email verified.'})


@extend_schema(tags=['auth'])
class EmailVerifyResendView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary='Resend the email-verification link to the current user')
    def post(self, request):
        if request.user.profile.is_email_verified:
            return success({'detail': 'Email is already verified.'})
        auth_services.send_verification_email(request.user)
        return success({'detail': 'Verification email sent.'})
