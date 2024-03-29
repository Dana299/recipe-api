from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from account.models import CustomUser


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid4(), ext)
    return filename


def get_default_expiration_date():
    return datetime.now(tz=timezone.utc) + timedelta(days=1)


class Image(models.Model):
    image = models.ImageField(
        upload_to=get_file_path,
        blank=True,
        null=True,
    )
    is_temporary = models.BooleanField(default=True)
    expiration_date = models.DateTimeField(default=get_default_expiration_date)

    def __str__(self):
        return self.image.url


class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


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

    name = models.CharField(max_length=100)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time_cooking = models.PositiveIntegerField(
        null=False,
        validators=[MinValueValidator(1),]
    )
    time_preparing = models.PositiveIntegerField(
        null=False,
        validators=[MinValueValidator(1),]
    )
    is_spicy = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    servings_number = models.PositiveIntegerField(
        null=False,
        validators=[MinValueValidator(1),]
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PUBLISHED
    )
    category = models.CharField(max_length=30, choices=Category.choices)
    time_created = models.DateTimeField(auto_now_add=True)
    main_picture = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f'{self.name} by {self.author.user_name}'


class RecipeStep(models.Model):

    text = models.TextField(max_length=500)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="steps",
    )
    image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'Step for recipe {self.recipe.id}'


class Comment(models.Model):
    text = models.TextField(max_length=1000)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # Если пользователь удален, его комментарии оставляем
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    time_created = models.DateTimeField(auto_now_add=True)

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
        return self.ingredient.name
