import re
import requests as http_requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()


def _unique_username(base):
    base = re.sub(r'[^\w]', '', base)[:20] or 'user'
    username, n = base, 1
    while User.objects.filter(username=username).exists():
        username = f'{base}{n}'
        n += 1
    return username


def _jwt(user):
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


def _get_or_create_social_user(email, defaults):
    user, created = User.objects.get_or_create(email=email, defaults=defaults)
    if created:
        user.set_unusable_password()
        user.save()
    return user


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.conf import settings as django_settings
        import logging
        logger = logging.getLogger(__name__)

        credential = request.data.get('credential')
        logger.warning('Google auth attempt — credential present: %s', bool(credential))
        if not credential:
            return Response({'error': 'credential is required'}, status=400)

        resp = http_requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': credential},
            timeout=10,
        )
        logger.warning('Google tokeninfo status: %s  body: %s', resp.status_code, resp.text[:300])
        if resp.status_code != 200:
            return Response({'error': f'Google token invalid: {resp.json().get("error_description", resp.text[:100])}'}, status=400)

        info = resp.json()

        if info.get('aud') != django_settings.GOOGLE_CLIENT_ID:
            logger.warning('Audience mismatch — got %s expected %s', info.get('aud'), django_settings.GOOGLE_CLIENT_ID)
            return Response({'error': f'Token audience mismatch: got {info.get("aud")}'}, status=400)

        email = info.get('email')
        if not email:
            return Response({'error': 'Google account has no email'}, status=400)

        user = _get_or_create_social_user(email, {
            'username': _unique_username(email.split('@')[0]),
            'first_name': info.get('given_name', ''),
            'last_name': info.get('family_name', ''),
        })
        return Response(_jwt(user))


class FacebookAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'access_token is required'}, status=400)

        resp = http_requests.get(
            'https://graph.facebook.com/me',
            params={'fields': 'id,first_name,last_name,email', 'access_token': access_token},
            timeout=10,
        )
        info = resp.json()
        if 'error' in info:
            return Response({'error': info['error']['message']}, status=400)

        fb_id = info.get('id', '')
        email = info.get('email') or f'fb_{fb_id}@facebook.com'

        user = _get_or_create_social_user(email, {
            'username': _unique_username(f'fb{fb_id}'),
            'first_name': info.get('first_name', ''),
            'last_name': info.get('last_name', ''),
        })
        return Response(_jwt(user))
