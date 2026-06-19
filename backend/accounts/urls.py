from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, LogoutView, MeView,
    GoogleAuthView, GoogleOAuthCallbackView,
    CookieTokenRefreshView,
    PasswordResetRequestView, PasswordResetConfirmView,
    EmailVerifyConfirmView, EmailVerifyResendView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),

    # Google SSO — two flows coexist:
    #   /google/          → legacy GSI popup (id_token in body)
    #   /google/callback/ → OAuth2 Authorization Code + PKCE (redirect flow)
    path('google/', GoogleAuthView.as_view(), name='auth-google'),
    path('google/callback/', GoogleOAuthCallbackView.as_view(), name='auth-google-oauth-callback'),

    # Token management
    path('token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('token/refresh/cookie/', CookieTokenRefreshView.as_view(), name='auth-token-refresh-cookie'),

    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),

    # Password reset
    path('password/reset/', PasswordResetRequestView.as_view(), name='auth-password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='auth-password-reset-confirm'),

    # Email verification
    path('email/verify/', EmailVerifyConfirmView.as_view(), name='auth-email-verify'),
    path('email/verify/resend/', EmailVerifyResendView.as_view(), name='auth-email-verify-resend'),
]
