from django import forms
from .models import EducationRequest

class EducationRequestForm(forms.ModelForm):
    class Meta:
        model = EducationRequest
        fields = ['full_name', 'age', 'education_level', 'reason']
        labels = {
            'full_name': 'Full Name',
            'age': 'Age',
            'education_level': 'Education Level',
            'reason': 'Reason for Support',
        }
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Explain why you need educational support...'}),
        }
