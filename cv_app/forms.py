from django import forms
from django.core.exceptions import ValidationError
from .models import CV, CVTemplate
import json


class CVForm(forms.ModelForm):
    class Meta:
        model = CV
        fields = [
            'title', 'template', 'full_name', 'job_title',
            'email', 'phone', 'location', 'links',
            'summary', 'skills', 'experience', 'education', 'projects'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Software Engineer CV'}),
            'full_name': forms.TextInput(attrs={'placeholder': 'John Doe'}),
            'job_title': forms.TextInput(attrs={'placeholder': 'Software Engineer'}),
            'email': forms.EmailInput(attrs={'placeholder': 'john@example.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '+1234567890'}),
            'location': forms.TextInput(attrs={'placeholder': 'New York, USA'}),
            'links': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'https://linkedin.com/in/johndoe\nhttps://github.com/johndoe'
            }),
            'summary': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Brief professional summary...'
            }),
            'skills': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Python, Django, JavaScript, React, SQL'
            }),
            # Hidden in UI; we will populate these from structured formsets in the view
            'experience': forms.Textarea(attrs={'rows': 1, 'style': 'display:none;'}),
            'education': forms.Textarea(attrs={'rows': 1, 'style': 'display:none;'}),
            'projects': forms.Textarea(attrs={'rows': 1, 'style': 'display:none;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = CVTemplate.objects.filter(active=True)
        # Ensure these are optional since we populate them programmatically
        self.fields['experience'].required = False
        self.fields['education'].required = False
        self.fields['projects'].required = False


class ExperienceItemForm(forms.Form):
    company = forms.CharField(max_length=200, required=False)
    position = forms.CharField(max_length=200, required=False)
    duration = forms.CharField(max_length=200, required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)


class EducationItemForm(forms.Form):
    institution = forms.CharField(max_length=200, required=False)
    degree = forms.CharField(max_length=200, required=False)
    duration = forms.CharField(max_length=200, required=False)
    status = forms.CharField(max_length=100, required=False)


class ProjectItemForm(forms.Form):
    name = forms.CharField(max_length=200, required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    technologies = forms.CharField(max_length=200, required=False)
    status = forms.CharField(max_length=100, required=False)
