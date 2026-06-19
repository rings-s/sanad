import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_CONTENT_MANAGER = 'content_manager'
    ROLE_SHEIKH = 'sheikh'

    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_CONTENT_MANAGER, 'Content Manager'),
        (ROLE_SHEIKH, 'Sheikh'),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER, db_index=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta(AbstractUser.Meta):
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @property
    def is_sheikh(self):
        return self.role == self.ROLE_SHEIKH

    @property
    def is_content_creator(self):
        return self.role in (self.ROLE_SHEIKH, self.ROLE_CONTENT_MANAGER)

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    is_email_verified = models.BooleanField(default=False)
    google_uid = models.CharField(max_length=200, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile({self.user.email})"
