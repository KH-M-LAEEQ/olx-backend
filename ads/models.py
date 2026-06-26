from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone

from categories.models import Category


class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('refurbished', 'Refurbished'),
    ]

    title       = models.CharField(max_length=255)
    description = models.TextField()
    price       = models.DecimalField(max_digits=12, decimal_places=2)
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='ads')
    seller      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ads')
    location    = models.CharField(max_length=200)
    condition   = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='used')
    is_active   = models.BooleanField(default=True)
    expires_at  = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.pk and not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=60)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return bool(self.expires_at and timezone.now() > self.expires_at)

    def __str__(self):
        return self.title


class AdImage(models.Model):
    ad       = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='images')
    image    = models.ImageField(upload_to='ads/')
    is_cover = models.BooleanField(default=False)

    def __str__(self):
        return f'Image for {self.ad.title}'


class Favourite(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favourites')
    ad         = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='favourited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ad')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} likes {self.ad.title}'


class AdReport(models.Model):
    REASON_CHOICES = [
        ('spam',          'Spam or misleading'),
        ('fraud',         'Fraud or scam'),
        ('inappropriate', 'Inappropriate content'),
        ('duplicate',     'Duplicate listing'),
        ('other',         'Other'),
    ]
    ad         = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reports')
    reporter   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reason     = models.CharField(max_length=20, choices=REASON_CHOICES)
    details    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ad', 'reporter')

    def __str__(self):
        return f'Report on {self.ad.title} by {self.reporter.username}'
