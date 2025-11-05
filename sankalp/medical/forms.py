from django import forms
from .models import MedicalCampRequest, Hospital

class MedicalCampForm(forms.ModelForm):
    class Meta:
        model = MedicalCampRequest
        fields = ['hospital', 'contact_person', 'phone', 'location', 'date', 'time', 'description']
        widgets = {
            'hospital': forms.Select(attrs={'class': 'form-select'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# 🌿 Form for volunteers to schedule an approved camp
class VolunteerScheduleForm(forms.ModelForm):
    class Meta:
        model = MedicalCampRequest
        fields = ['scheduled_date']  # ✅ only include existing fields
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
