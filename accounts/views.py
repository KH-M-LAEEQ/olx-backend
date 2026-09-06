import logging

from django.conf import settings as django_settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, PasswordResetToken, ContactMessage
from .serializers import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)

OTP_EXPIRY_HOURS = 24


class AuthRateThrottle(AnonRateThrottle):
    rate = '5/minute'


def _send_otp_email(user, otp):
    if not user.email:
        return
    subject = 'Your Bazaario Email Verification Code'
    body = (
        f'Hi {user.username},\n\n'
        f'Your Bazaario email verification code is:\n\n'
        f'    {otp}\n\n'
        f'This code expires in {OTP_EXPIRY_HOURS} hours.\n\n'
        f'If you did not create a Bazaario account, ignore this email.\n\n'
        f'— The Bazaario Team'
    )
    try:
        send_mail(subject, body, django_settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    except Exception as exc:
        logger.error('Failed to send verification OTP to %s: %s', user.email, exc)


def _send_reset_otp_email(user, otp):
    if not user.email:
        return
    subject = 'Your Bazaario Password Reset Code'
    body = (
        f'Hi {user.username},\n\n'
        f'Your Bazaario password reset code is:\n\n'
        f'    {otp}\n\n'
        f'This code expires in {OTP_EXPIRY_HOURS} hours.\n\n'
        f'If you did not request a password reset, ignore this email.\n\n'
        f'— The Bazaario Team'
    )
    try:
        send_mail(subject, body, django_settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    except Exception as exc:
        logger.error('Failed to send reset OTP to %s: %s', user.email, exc)


class RegisterView(generics.CreateAPIView):
    queryset           = User.objects.all()
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [AuthRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        from .models import EmailVerificationToken
        ev = EmailVerificationToken.objects.create(user=user)
        _send_otp_email(user, ev.otp)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user':    UserSerializer(user, context={'request': request}).data,
            'refresh': str(refresh),
            'access':  str(refresh.access_token),
        }, status=201)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
        except Exception:
            pass
        return Response({'detail': 'Logged out.'})


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [AuthRateThrottle]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response({'detail': 'Email is required.'}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal whether email exists — same response either way
            return Response({'detail': 'If that email is registered, a reset code has been sent.'})

        PasswordResetToken.objects.filter(user=user, used=False).delete()
        reset = PasswordResetToken.objects.create(user=user)
        _send_reset_otp_email(user, reset.otp)

        using_smtp = bool(django_settings.EMAIL_HOST_USER)
        return Response({
            'detail': 'If that email is registered, a reset code has been sent.',
            # Only expose OTP in dev (console backend). Never expose when real email is configured.
            'otp': reset.otp if not using_smtp else None,
        })


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [AuthRateThrottle]

    def post(self, request):
        email     = request.data.get('email', '').strip()
        otp       = request.data.get('otp', '').strip()
        password  = request.data.get('password', '')
        password2 = request.data.get('password2', '')

        if not all([email, otp, password, password2]):
            return Response({'detail': 'email, otp, password, and password2 are required.'}, status=400)
        if password != password2:
            return Response({'password': 'Passwords do not match.'}, status=400)
        if not otp.isdigit() or len(otp) != 6:
            return Response({'detail': 'Enter the 6-digit code.'}, status=400)

        try:
            user = User.objects.get(email=email)
            reset = PasswordResetToken.objects.select_related('user').get(otp=otp, user=user, used=False)
        except (User.DoesNotExist, PasswordResetToken.DoesNotExist):
            return Response({'detail': 'Incorrect code or email.'}, status=400)

        if not reset.is_valid():
            return Response({'detail': 'Code has expired. Please request a new one.'}, status=400)

        try:
            validate_password(password, reset.user)
        except ValidationError as e:
            return Response({'password': list(e.messages)}, status=400)

        reset.user.set_password(password)
        reset.user.save()
        reset.used = True
        reset.save()
        return Response({'detail': 'Password reset successfully. You can now log in.'})


class ContactView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name    = request.data.get('name', '').strip()
        email   = request.data.get('email', '').strip()
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()

        errors = {}
        if not name:    errors['name']    = 'Name is required.'
        if not subject: errors['subject'] = 'Subject is required.'
        if not message: errors['message'] = 'Message is required.'
        if not email:
            errors['email'] = 'Email is required.'
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = 'Enter a valid email address.'
        if errors:
            return Response(errors, status=400)

        ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
        return Response({'detail': 'Message received. We will get back to you within 24 hours.'}, status=201)


class SendVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes   = [AuthRateThrottle]

    def post(self, request):
        from .models import EmailVerificationToken
        if request.user.is_email_verified:
            return Response({'detail': 'Email is already verified.'})
        EmailVerificationToken.objects.filter(user=request.user).delete()
        ev = EmailVerificationToken.objects.create(user=request.user)
        _send_otp_email(request.user, ev.otp)
        using_smtp = bool(django_settings.EMAIL_HOST_USER)
        return Response({
            'detail': f'OTP sent to {request.user.email}.' if using_smtp else 'OTP generated (check server console).',
            'otp': ev.otp if not using_smtp else None,
        })


class VerifyEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes   = [AuthRateThrottle]

    def post(self, request):
        from .models import EmailVerificationToken
        otp = (request.data.get('otp') or '').strip()
        if not otp or not otp.isdigit() or len(otp) != 6:
            return Response({'detail': 'Enter the 6-digit OTP.'}, status=400)
        try:
            ev = EmailVerificationToken.objects.select_related('user').get(otp=otp, user=request.user)
        except EmailVerificationToken.DoesNotExist:
            return Response({'detail': 'Incorrect OTP.'}, status=400)
        if not ev.is_valid():
            return Response({'detail': 'OTP has expired. Please request a new one.'}, status=400)
        ev.user.is_email_verified = True
        ev.user.save()
        ev.delete()
        return Response({'detail': 'Email verified successfully.'})
