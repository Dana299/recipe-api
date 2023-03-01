import re

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from PIL import Image as PillowImage
from rest_framework import serializers

from .models import (Comment, Image, Ingredient, Recipe, RecipeIngredient,
                     RecipeStep)


class StorageURLField(serializers.Field):
    """
    Field that contains image URL from storage
    and that is converted into Image model object
    """

    S3_URL_REGEX = (rf'{settings.AWS_S3_ENDPOINT_URL}/'
                    f'{settings.AWS_STORAGE_BUCKET_NAME}/'
                    f'{settings.AWS_LOCATION}.+$')

    def to_internal_value(self, url):
        """
        Return the corresponding Image object from the database for the given URL.
        Raises ValidationError if URL does not match the expected pattern S3_URL_REGEX.
        Raises ValidationError if corresponding Image object does not exist in DB.
        """

        if not re.fullmatch(self.S3_URL_REGEX, url):
            raise serializers.ValidationError("Invalid URL.")

        filename = url.split('/')[-1]

        try:
            obj = Image.objects.get(image=filename)
            return obj
        except Image.DoesNotExist:
            raise serializers.ValidationError("Such file does not exist")
        else:
            raise serializers.ValidationError("Invalid file URL")

    def to_representation(self, value):
        """
        Returns image url
        """
        return str(value)


class ImagePostSerializer(serializers.ModelSerializer):
    """
    Serializer for images apart
    """
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = ('image',)

    def validate_image(self, image):
        """ Checks whether the image format is supported. """

        try:
            with PillowImage.open(image) as img:
                if img.format not in settings.ALLOWED_UPLOAD_IMAGES:
                    raise serializers.ValidationError(
                        _('Unsupported image format. Only JPEG and PNG are supported.')
                    )
        except IOError:
            raise serializers.ValidationError('Invalid image file.')

        return image


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Serializer for a list of recipes on home page
    """
    main_picture = StorageURLField()
    author = serializers.StringRelatedField()

    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'category',
            'is_spicy',
            'is_vegetarian',
            'servings_number',
            'main_picture',
        )


class StepSerializer(serializers.ModelSerializer):
    """
    Serializer for recipe steps
    """
    image = StorageURLField(required=False)

    class Meta:
        model = RecipeStep
        fields = ('text', 'image',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for ingredients in recipes
    """
    ingredient = serializers.CharField()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'unit', 'amount')

    def validate_ingredient(self, value):
        """
        Check if the ingredient already exists in the database
        """
        if not Ingredient.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Ingredient '{value}' does not exist.")
        return value


class RecipeDetailedSerializer(serializers.ModelSerializer):
    """
    Serializer for a certain recipe - more fields included
    """
    main_picture = StorageURLField(required=True)
    ingredients = RecipeIngredientSerializer(many=True)
    steps = StepSerializer(many=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Recipe
        fields = (
            'name',
            'author',
            'category',
            'is_spicy',
            'is_vegetarian',
            'servings_number',
            'time_cooking',
            'time_preparing',
            'time_created',
            'main_picture',
            'ingredients',
            'steps',
        )

    def validate(self, data):
        """
        Check if recipe has ingredients and steps
        """
        ingredients = data['ingredients']
        steps = data['steps']
        if len(ingredients) == 0:
            raise serializers.ValidationError('Recipe must have at least one ingredient')
        if len(steps) == 0:
            raise serializers.ValidationError('Recipe must have at least one step')
        return data

    def create(self, validated_data):
        # get author from request
        validated_data['author'] = self.context['request'].user
        # pop ingredients and steps
        ingredients_list = validated_data.pop('ingredients', [])
        steps_list = validated_data.pop('steps', [])
        # create recipe instance
        recipe_obj = Recipe.objects.create(**validated_data)

        # create ingedients and connections
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe_obj,
                ingredient=Ingredient.objects.get(
                    name=ingredient_dict['ingredient']
                ),
                unit=ingredient_dict["unit"],
                amount=ingredient_dict["amount"],
            ) for ingredient_dict in ingredients_list
        ]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe_obj.ingredients.set(recipe_ingredients)

        # create steps
        steps_in_recipe = [
            RecipeStep(
                text=step_dict['text'],
                recipe=recipe_obj,
                image=step_dict.get('image', None)
            ) for step_dict in steps_list
        ]

        RecipeStep.objects.bulk_create(steps_in_recipe)
        recipe_obj.steps.set(steps_in_recipe)

        # change image flag 'is_temporary' to False
        image = recipe_obj.main_picture
        image.is_temporary = False
        image.save()

        return recipe_obj

    def update(self, instance, validated_data):
        ingredients_list = validated_data.pop('ingredients')
        steps_list = validated_data.pop('steps')

        instance.name = validated_data.get('name')
        instance.time_cooking = validated_data.get('time_cooking')
        instance.time_preparing = validated_data.get('time_preparing')
        instance.is_spicy = validated_data.get('is_spicy')
        instance.is_vegetarian = validated_data.get('is_vegetarian')
        instance.servings_number = validated_data.get('servings_number')
        instance.status = validated_data.get('status')
        instance.category = validated_data.get('category')
        instance.main_picture = validated_data.get('main_picture')

        # delete existing steps and ingredient connections from DB
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeStep.objects.filter(recipe=instance).delete()

        # create ingedients and connections
        recipe_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=Ingredient.objects.get(
                    name=ingredient_dict['ingredient']
                ),
                unit=ingredient_dict["unit"],
                amount=ingredient_dict["amount"],
            ) for ingredient_dict in ingredients_list
        ]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        instance.ingredients.set(recipe_ingredients)

        # create steps
        steps_in_recipe = [
            RecipeStep(
                text=step_dict['text'],
                recipe=instance,
                image=step_dict['image']
            ) for step_dict in steps_list
        ]

        RecipeStep.objects.bulk_create(steps_in_recipe)
        instance.steps.set(steps_in_recipe)

        return instance


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments
    """
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ('text', 'user', 'time_created')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['recipe'] = get_object_or_404(
            Recipe,
            pk=self.context['recipe_pk'],
        )
        return super().create(validated_data)