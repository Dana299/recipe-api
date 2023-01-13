# Generated by Django 4.1.4 on 2023-01-10 16:08

from django.db import migrations, models
import django.db.models.deletion
import myproject.storage_backends
import recipe_api.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_api', '0004_alter_recipe_servings_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(storage=myproject.storage_backends.ClientDocsStorage(), upload_to=recipe_api.models.get_file_path),
        ),
        migrations.AlterField(
            model_name='recipestep',
            name='image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='recipe_api.image'),
        ),
    ]