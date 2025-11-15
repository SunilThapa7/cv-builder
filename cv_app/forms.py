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
            'experience': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'JSON format: [{"company": "ABC Corp", "position": "Developer", "duration": "2020-2023", "description": "Developed features..."}]'
            }),
            'education': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'JSON format: [{"institution": "University", "degree": "BS Computer Science", "duration": "2016-2020"}]'
            }),
            'projects': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'JSON format: [{"name": "Project Name", "description": "Description...", "technologies": "React, Node.js"}]'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = CVTemplate.objects.filter(active=True)

    def _validate_json_list(self, value, field_label):
        """
        Validate that value is either empty or a JSON array (list). Returns normalized JSON string.
        """
        if not value:
            return value
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"{field_label} must be valid JSON. Example: [{{\"key\": \"value\"}}]. Error: {e.msg}")
        if not isinstance(parsed, list):
            raise ValidationError(f"{field_label} must be a JSON array (e.g., [{{...}}, {{...}}]).")
        # Normalize to a compact JSON string to keep storage consistent
        return json.dumps(parsed, ensure_ascii=False)

    def clean_experience(self):
        value = self.cleaned_data.get('experience', '')
        return self._validate_json_list(value, 'Experience')

    def clean_education(self):
        value = self.cleaned_data.get('education', '')
        return self._validate_json_list(value, 'Education')

    def clean_projects(self):
        value = self.cleaned_data.get('projects', '')
        return self._validate_json_list(value, 'Projects')
