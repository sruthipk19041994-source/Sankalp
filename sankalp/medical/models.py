from django.db import models
from django.conf import settings
import uuid

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class MedicalCampRequest(models.Model):
    volunteer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)

    description = models.TextField()
    approval_status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateField(null=True, blank=True)

    # ✅ Unique token for hospital approval link (safe to migrate)
    approval_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.hospital.name} - {self.date}"
