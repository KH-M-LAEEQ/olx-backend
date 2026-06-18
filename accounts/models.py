from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone   = models.CharField(max_length=20, blank=True)
    city    = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    avatar  = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username
