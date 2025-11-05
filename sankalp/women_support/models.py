from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings

# 🌸 1️⃣ Women Awareness Campaign (same as Legal Camp Request)
class WomenSupportCampaign(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Scheduled', 'Scheduled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=150)
    proposed_date = models.DateField(null=True, blank=True)
    proposed_time = models.TimeField(null=True, blank=True)

    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)  # ✅ NEW FIELD
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    volunteer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='women_campaigns'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_women_support_campaigns'
    )
    supporter = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='supported_women_campaigns'
)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# 🌸 2️⃣ Women Awareness Articles (Supporter writes informative articles)
class WomenSupportArticle(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='women_articles'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class WomenSupportQuestion(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Answered', 'Answered'),
    ]

    asked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='women_questions'
    )
    question = models.TextField()
    allow_anonymous = models.BooleanField(default=False)
    answer = models.TextField(blank=True, null=True)
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='women_answers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    # ✅ New field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
      return self.question[:50]
