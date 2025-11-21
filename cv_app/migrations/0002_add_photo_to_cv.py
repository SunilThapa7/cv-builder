from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cv_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cv",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="photos/"),
        ),
    ]
