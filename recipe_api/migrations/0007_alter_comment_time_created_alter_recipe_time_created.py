# Generated by Django 4.1.4 on 2023-01-31 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_api', '0006_alter_image_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='time_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='time_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
