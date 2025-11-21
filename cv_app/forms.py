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
                'placeholder': 'Either JSON array OR simple lines, one per item:\nCompany | Position | Duration | Description\nABC Corp | Developer | 2020-2023 | Built features...'
            }),
            'education': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Either JSON array OR simple lines, one per item:\nInstitution | Degree | Duration\nState Univ | BSc CS | 2016-2020'
            }),
            'projects': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Either JSON array OR simple lines, one per item:\nName | Description | Technologies\nPortfolio Site | Personal site | React, Node.js'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['template'].queryset = CVTemplate.objects.filter(active=True)

    def _try_parse_json_list(self, value, field_label):
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            raise ValidationError(f"{field_label} must be a JSON array (e.g., [{{...}}, {{...}}]).")
        except json.JSONDecodeError:
            return None  # Not JSON; caller may try simple parsing

    def _parse_pipe_lines(self, value, fields, field_label):
        items = []
        for line in value.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split('|')]
            # Pad/truncate to expected length
            if len(parts) < len(fields):
                parts += [''] * (len(fields) - len(parts))
            elif len(parts) > len(fields):
                parts = parts[:len(fields)]
            item = {fname: parts[i] for i, fname in enumerate(fields)}
            items.append(item)
        if not items and value.strip():
            raise ValidationError(f"{field_label} format: use 'A | B | C | ...' per line, or provide a JSON array.")
        return items

    def _normalize_to_json(self, items):
        return json.dumps(items, ensure_ascii=False)

    def clean_experience(self):
        value = self.cleaned_data.get('experience', '')
        if not value:
            return ''
        parsed = self._try_parse_json_list(value, 'Experience')
        if parsed is None:
            parsed = self._parse_pipe_lines(value, ['company', 'position', 'duration', 'description'], 'Experience')
        return self._normalize_to_json(parsed)

    def clean_education(self):
        value = self.cleaned_data.get('education', '')
        if not value:
            return ''
        parsed = self._try_parse_json_list(value, 'Education')
        if parsed is None:
            parsed = self._parse_pipe_lines(value, ['institution', 'degree', 'duration'], 'Education')
        return self._normalize_to_json(parsed)

    def clean_projects(self):
        value = self.cleaned_data.get('projects', '')
        if not value:
            return ''
        parsed = self._try_parse_json_list(value, 'Projects')
        if parsed is None:
            parsed = self._parse_pipe_lines(value, ['name', 'description', 'technologies'], 'Projects')
        return self._normalize_to_json(parsed)
