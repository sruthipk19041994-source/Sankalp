from django import forms
from .models import WomenSupportCampaign, WomenSupportArticle, WomenSupportQuestion


# 🌸 1️⃣ Volunteer — Request Campaign
from django import forms
from .models import WomenSupportCampaign
from django.contrib.auth import get_user_model

User = get_user_model()

class CampaignRequestForm(forms.ModelForm):
    supporter = forms.ModelChoiceField(
        queryset=User.objects.filter(role='Supporter'),
        label="Select Supporter",
        required=True
    )

    class Meta:
        model = WomenSupportCampaign
        fields = ['title', 'description', 'location', 'proposed_date', 'proposed_time', 'supporter']
        widgets = {
            'proposed_date': forms.DateInput(attrs={'type': 'date'}),
            'proposed_time': forms.TimeInput(attrs={'type': 'time'}),
        }

            # CampaignApprovalForm
class CampaignApprovalForm(forms.ModelForm):
    class Meta:
        model = WomenSupportCampaign
        fields = ['status', 'scheduled_date', 'scheduled_time']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'type': 'time'}),
        }

        


# 🌸 3️⃣ Supporter — Add or Edit Awareness Articles
class WomenSupportArticleForm(forms.ModelForm):
    class Meta:
        model = WomenSupportArticle
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


# 🌸 4️⃣ Beneficiary — Ask Questions
class WomenSupportQuestionForm(forms.ModelForm):
    class Meta:
        model = WomenSupportQuestion
        fields = ['question', 'allow_anonymous']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3}),
        }


# 🌸 5️⃣ Supporter — Answer Questions
class WomenSupportAnswerForm(forms.ModelForm):
    class Meta:
        model = WomenSupportQuestion
        fields = ['answer']
        widgets = {
            'answer': forms.Textarea(attrs={'rows': 4}),
        }
