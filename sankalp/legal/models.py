from django.db import models
from django.conf import settings


class LegalAwarenessCamp(models.Model):
    CATEGORY_CHOICES = [
        ('SheRights', 'Women’s Rights'),
        ('KisanKanoon', 'Farmers’ Rights'),
        ('KnowYourRights', 'Student Rights'),
        ('WorkShield', 'Employee Rights'),
        ('LawLink', 'General Public Rights'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='LawLink')
    location = models.CharField(max_length=100)
    proposed_date = models.DateField()
    proposed_time = models.TimeField(null=True, blank=True)

    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)


    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_legal_camps'
    )

    assigned_advocate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_legal_camps',
        limit_choices_to={'role': 'Advocate'}
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    allow_anonymous = models.BooleanField(default=False)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    supporting_document = models.FileField(upload_to='legal_docs/', null=True, blank=True)

    # ✅ Audit & metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.category})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Legal Awareness Camp"
        verbose_name_plural = "Legal Awareness Camps"


class LegalArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class LegalQuestion(models.Model):
    asked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='answered_questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    is_answered = models.BooleanField(default=False)  # ✅ add this

    def __str__(self):
        return f"Q: {self.question[:50]}..."
