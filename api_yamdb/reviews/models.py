from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=USER)
    confirmation_code = models.CharField(max_length=10, blank=True, null=True)
