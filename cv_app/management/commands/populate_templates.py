from django.core.management.base import BaseCommand
from cv_app.models import CVTemplate

class Command(BaseCommand):
    help = 'Populate CV templates'

    def handle(self, *args, **kwargs):
        templates = [
            {'slug': 'classic', 'name': 'Classic', 'preview_image': 'img/template_previews/classic.png'},
            {'slug': 'modern', 'name': 'Modern', 'preview_image': 'img/template_previews/modern.png'},
            {'slug': 'minimal', 'name': 'Minimal', 'preview_image': 'img/template_previews/minimal.png'},
        ]

        for template_data in templates:
            CVTemplate.objects.get_or_create(
                slug=template_data['slug'],
                defaults=template_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated templates'))
