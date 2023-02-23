# Generated by Django 4.1.4 on 2023-02-01 13:20

from django.db import migrations, models
import myproject.storage_backends
import recipe_api.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_api', '0007_alter_comment_time_created_alter_recipe_time_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=myproject.storage_backends.ClientImageStorage(), upload_to=recipe_api.models.get_file_path),
        ),
    ]
