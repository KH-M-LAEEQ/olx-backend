import random
import uuid
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone


def _generate_otp():
    return str(random.randint(100000, 999999))


class User(AbstractUser):
    phone              = models.CharField(max_length=20, blank=True)
    city               = models.CharField(max_length=100, blank=True)
    address            = models.TextField(blank=True)
    avatar             = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_email_verified  = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class EmailVerificationToken(models.Model):
    user       = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_verification')
    otp        = models.CharField(max_length=6, default=_generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (timezone.now() - self.created_at).total_seconds() < 86400  # 24 hours

    def __str__(self):
        return f'OTP for {self.user.username}'


class PasswordResetToken(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reset_tokens')
    otp        = models.CharField(max_length=6, default=_generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)
    used       = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and (timezone.now() - self.created_at).total_seconds() < 86400

    def __str__(self):
        return f'Reset OTP for {self.user.username}'


class ContactMessage(models.Model):
    name       = models.CharField(max_length=200)
    email      = models.EmailField()
    subject    = models.CharField(max_length=300)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.subject}'
