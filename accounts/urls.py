from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, LogoutView, PasswordResetView, PasswordResetConfirmView, ContactView, SendVerificationView, VerifyEmailView
from .social_auth import GoogleAuthView, FacebookAuthView

urlpatterns = [
    path('register/',               RegisterView.as_view(),              name='register'),
    path('login/',                  TokenObtainPairView.as_view(),       name='token_obtain_pair'),
    path('refresh/',                TokenRefreshView.as_view(),          name='token_refresh'),
    path('logout/',                 LogoutView.as_view(),                name='logout'),
    path('profile/',                ProfileView.as_view(),               name='profile'),
    path('google/',                 GoogleAuthView.as_view(),            name='google_auth'),
    path('facebook/',               FacebookAuthView.as_view(),          name='facebook_auth'),
    path('password-reset/',         PasswordResetView.as_view(),         name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(),  name='password_reset_confirm'),
    path('contact/',                ContactView.as_view(),               name='contact'),
    path('send-verification/',      SendVerificationView.as_view(),      name='send_verification'),
    path('verify-email/',           VerifyEmailView.as_view(),           name='verify_email'),
]
