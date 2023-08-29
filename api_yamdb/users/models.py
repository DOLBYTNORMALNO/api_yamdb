from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLE_CHOICES = [
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name="Role"
    )
    confirmation_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Confirmation Code"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Bio"
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        verbose_name = "custom user"
        verbose_name_plural = "custom users"

    def __str__(self):
        return self.username
