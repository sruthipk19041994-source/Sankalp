from django import forms
from .models import LegalAwarenessCamp,LegalArticle,LegalQuestion


class LegalAwarenessCampForm(forms.ModelForm):
    class Meta:
        model = LegalAwarenessCamp
        fields = [
            'title',
            'description',
            'category',
            'location',
            'proposed_date',
            'proposed_time',   # ✅ Add this
            'allow_anonymous',
            'contact_number',
            'supporting_document',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter camp title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'proposed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'proposed_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),  # optional: add class
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional contact number'}),
        }



class LegalArticleForm(forms.ModelForm):
    class Meta:
        model = LegalArticle
        fields = ['title', 'content']


class LegalQuestionForm(forms.ModelForm):
    class Meta:
        model = LegalQuestion
        fields = ['question']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your legal question here...'}),}