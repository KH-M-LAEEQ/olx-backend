from django.db import models
from django.conf import settings
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
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AdImage(models.Model):
    ad        = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='images')
    image     = models.ImageField(upload_to='ads/')
    is_cover  = models.BooleanField(default=False)

    def __str__(self):
        return f'Image for {self.ad.title}'
