# Generated by Django 4.1.4 on 2023-02-23 14:02

from django.db import migrations, models
import recipe_api.models


class Migration(migrations.Migration):
    dependencies = [
        ("recipe_api", "0009_rename_comment_text_comment_text_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to=recipe_api.models.get_file_path
            ),
        ),
    ]
