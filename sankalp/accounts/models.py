from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class RoleChoices(models.TextChoices):
    ADMIN = 'Admin', 'Admin'
    VOLUNTEER = 'Volunteer', 'Volunteer'
    DONOR = 'Donor', 'Donor'
    BENEFICIARY = 'Beneficiary', 'Beneficiary'
    SUPPORTER = 'Supporter', 'Supporter'
    ADVOCATE = 'Advocate', 'Advocate'


class Profile(AbstractUser):
    role = models.CharField(max_length=50, choices=RoleChoices.choices)
    contact = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)  # ✅ Added for forgot-password

    def __str__(self):
        return f"{self.username} ({self.role})"


class Notification(models.Model):
    """
    Simple per-user notification stored in DB.
    Use Profile as recipient (consistent with your project).
    """
    recipient = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification to {self.recipient} — {'read' if self.is_read else 'unread'}"
