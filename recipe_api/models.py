import os
from decimal import Decimal
from uuid import uuid1

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from account.models import CustomUser


def get_image_path(instance, filename):
    """"
    Custom upload_to function to make filepaths for images
    """
    result = os.path.join('images', str(instance.pk), uuid1().hex)
    if '.' in filename:
        result = os.path.join(result, filename.split('.')[-1])
    return result


class Ingredient(models.Model):
    ingredient_name = models.CharField(max_length=50)

    def __str__(self):
        return self.ingredient_name


class Recipe(models.Model):

    class Status(models.TextChoices):
        DRAFT = "Draft"
        PUBLISHED = "Published"
        MODERATION = "Moderation"

    class Category(models.TextChoices):
        DRINKS = "Drinks"
        SOUP = "Soups"
        DESSERT = "Desserts"
        COLD_APPETIZERS = "Cold appetizers"
        HOT_APPETIZERS = "Hot appetizers"
        BREAKFAST = "Breakfast"
        MAIN_COURSE = "Main course"
        SIDE_DISH = "Side dishes"
        SALAD = "Salads"
        PASTRY = "Pastries"
        BREAD = "Breads"

    recipe_name = models.CharField(max_length=100)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time_cooking = models.PositiveIntegerField(null=False)
    time_preparing = models.PositiveIntegerField(null=False)
    is_spicy = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PUBLISHED
    )
    category = models.CharField(max_length=30, choices=Category.choices)
    time_created = models.DateTimeField(default=timezone.now)
    main_picture = models.ImageField(upload_to=get_image_path)

    def __str__(self):
        return f'{self.recipe_name} by {self.author.user_name}'


class RecipeStep(models.Model):

    step_text = models.TextField(max_length=500, blank=True)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    image_url = models.ImageField(
        upload_to=get_image_path,
        blank=True,
        null=True
    )

    def __str__(self):
        return f'Step for recipe {self.recipe.id}'


class Comment(models.Model):
    comment_text = models.TextField(max_length=1000)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # Если пользователь удален, его комментарии оставляем
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    time_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)


class RecipeIngredient(models.Model):

    class UnitOptions(models.TextChoices):
        KILOGRAM = "kg"
        GRAM = "g"
        LITER = "l"
        MILLILITER = "ml"
        TABLE_SPOON = "tbsp"
        TEA_SPOON = "tsp"

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
    )
    unit = models.CharField(max_length=10, choices=UnitOptions.choices)
    amount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    def __str__(self):
        return self.ingredient.ingredient_name
