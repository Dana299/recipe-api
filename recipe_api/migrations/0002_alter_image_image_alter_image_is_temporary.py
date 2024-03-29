# Generated by Django 4.1.4 on 2023-01-03 21:30

from django.db import migrations, models

import myproject.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ("recipe_api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="image",
            field=models.ImageField(
                storage=myproject.storage_backends.ClientImageStorage(), upload_to=""
            ),
        ),
        migrations.AlterField(
            model_name="image",
            name="is_temporary",
            field=models.BooleanField(default=True),
        ),
    ]
