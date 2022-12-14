# Generated by Django 4.1.4 on 2022-12-14 20:11

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import recipe_api.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Ingredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ingredient_name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Recipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("recipe_name", models.CharField(max_length=100)),
                ("time_cooking", models.PositiveIntegerField()),
                ("time_preparing", models.PositiveIntegerField()),
                ("is_spicy", models.BooleanField(default=False)),
                ("is_vegetarian", models.BooleanField(default=False)),
                ("servings_number", models.PositiveIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Draft", "Draft"),
                            ("Published", "Published"),
                            ("Moderation", "Moderation"),
                        ],
                        default="Published",
                        max_length=10,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("Drinks", "Drinks"),
                            ("Soups", "Soup"),
                            ("Desserts", "Dessert"),
                            ("Cold appetizers", "Cold Appetizers"),
                            ("Hot appetizers", "Hot Appetizers"),
                            ("Breakfast", "Breakfast"),
                            ("Main course", "Main Course"),
                            ("Side dishes", "Side Dish"),
                            ("Salads", "Salad"),
                            ("Pastries", "Pastry"),
                            ("Breads", "Bread"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "time_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "main_picture",
                    models.ImageField(upload_to=recipe_api.models.get_image_path),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecipeStep",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("step_text", models.TextField(blank=True, max_length=500)),
                (
                    "image_url",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=recipe_api.models.get_image_path,
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="steps",
                        to="recipe_api.recipe",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecipeIngredient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "unit",
                    models.CharField(
                        choices=[
                            ("kg", "Kilogram"),
                            ("g", "Gram"),
                            ("l", "Liter"),
                            ("ml", "Milliliter"),
                            ("tbsp", "Table Spoon"),
                            ("tsp", "Tea Spoon"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=5,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0.01"))
                        ],
                    ),
                ),
                (
                    "ingredient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="recipe_api.ingredient",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ingredients",
                        to="recipe_api.recipe",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("comment_text", models.TextField(max_length=1000)),
                (
                    "time_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="recipe_api.recipe",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
