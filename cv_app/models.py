from django.db import models
from django.contrib.auth.models import User
import json


class CVTemplate(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    preview_image = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CV(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cvs')
    title = models.CharField(max_length=200)
    template = models.ForeignKey(CVTemplate, on_delete=models.SET_NULL, null=True)

    # Personal Information
    full_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)
    links = models.TextField(blank=True, help_text="LinkedIn, GitHub, Portfolio (one per line)")

    # Summary
    summary = models.TextField(blank=True)

    # Skills
    skills = models.TextField(blank=True, help_text="Comma-separated or grouped")

    # Experience (JSON field)
    experience = models.TextField(blank=True, help_text="JSON format")

    # Education (JSON field)
    education = models.TextField(blank=True, help_text="JSON format")

    # Projects (JSON field)
    projects = models.TextField(blank=True, help_text="JSON format")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.owner.username}"

    def get_experience_list(self):
        if self.experience:
            try:
                return json.loads(self.experience)
            except json.JSONDecodeError:
                return []
        return []

    def get_education_list(self):
        if self.education:
            try:
                return json.loads(self.education)
            except json.JSONDecodeError:
                return []
        return []

    def get_projects_list(self):
        if self.projects:
            try:
                return json.loads(self.projects)
            except json.JSONDecodeError:
                return []
        return []

    def get_links_list(self):
        if self.links:
            return [link.strip() for link in self.links.split('\n') if link.strip()]
        return []
