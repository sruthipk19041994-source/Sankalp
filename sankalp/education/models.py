from django.db import models
from django.utils import timezone
from accounts.models import Profile
from django.conf import settings  # ✅ to access env secrets later

class EducationRequest(models.Model):
    beneficiary = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education_requests')
    full_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)
    education_level = models.CharField(max_length=100)
    reason = models.TextField()

    # ✅ status lifecycle: Pending → Forwarded → Approved/Rejected
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Forwarded', 'Forwarded'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)

    # 👇 Volunteer & donor linkage
    volunteer = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='volunteer_forwarded_requests')
    forwarded_to = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='donor_received_requests')

    forwarded_at = models.DateTimeField(null=True, blank=True)
    decision_at = models.DateTimeField(null=True, blank=True)

    # ✅ optional volunteer/admin notes
    volunteer_notes = models.TextField(null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} ({self.status})"
