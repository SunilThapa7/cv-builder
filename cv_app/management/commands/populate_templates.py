from django.core.management.base import BaseCommand
from cv_app.models import CVTemplate

class Command(BaseCommand):
    help = 'Populate CV templates'

    def handle(self, *args, **kwargs):
        templates = [
            {'slug': 'classic', 'name': 'Classic', 'preview_image': 'img/template_previews/classic.png'},
            {'slug': 'modern', 'name': 'Modern', 'preview_image': 'img/template_previews/modern.png'},
            {'slug': 'minimal', 'name': 'Minimal', 'preview_image': 'img/template_previews/minimal.png'},
            {'slug': 'advanced', 'name': 'Advanced', 'preview_image': 'img/template_previews/advanced.png'},
        ]

        for template_data in templates:
            obj, created = CVTemplate.objects.get_or_create(
                slug=template_data['slug'],
                defaults=template_data
            )
            # Update existing rows to keep preview images and names in sync
            if not created:
                updated = False
                if obj.name != template_data['name']:
                    obj.name = template_data['name']
                    updated = True
                if obj.preview_image != template_data['preview_image']:
                    obj.preview_image = template_data['preview_image']
                    updated = True
                if updated:
                    obj.save()

        self.stdout.write(self.style.SUCCESS('Successfully populated templates'))
