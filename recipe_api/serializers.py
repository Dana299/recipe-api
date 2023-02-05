import io
import re
import sys

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.translation import gettext_lazy as _
from PIL import Image as PillowImage
from rest_framework import serializers

from .models import (Comment, Image, Ingredient, Recipe, RecipeIngredient,
                     RecipeStep)


class ImageURLField(serializers.Field):
    """
    Field that contains image URL from storage
    and that is converted into Image model object
    """
    def to_internal_value(self, data):
        filename = re.search(r'[^\/]*\.jpeg', data)
        if filename:
            try:
                obj = Image.objects.get(image=filename.group(0))
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
        # converting into PNG format
        img = PillowImage.open(image)
        img_name = image.name.split('.')[0]

        if img.format.lower() not in settings.ALLOWED_UPLOAD_IMAGES:
            raise serializers.ValidationError(
                _("Unsupported file format. Supported formats are %s."
                  % ", ".join(settings.ALLOWED_UPLOAD_IMAGES))
            )

        if img.format.lower() != 'jpeg':
            img_io = io.BytesIO()
            img = img.convert('RGB')
            img.save(img_io, format='jpeg', quality=40)

            converted_img = InMemoryUploadedFile(
                file=img_io,
                field_name='ImageField',
                name=img_name + '.jpeg',
                size=sys.getsizeof(img_io),
                content_type='png',
                charset=None
            )

            return converted_img


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Serializer for a list of recipes on home page
    """
    main_picture = ImageURLField()

    class Meta:
        model = Recipe
        fields = (
            'recipe_name',
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
    image = ImageURLField(required=False)

    class Meta:
        model = RecipeStep
        fields = ('step_text', 'image',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for ingredients in recipes
    """
    ingredient = serializers.CharField()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'unit', 'amount')


class RecipeDetailedSerializer(serializers.ModelSerializer):
    """
    Serializer for a certain recipe - more fields included
    """
    main_picture = ImageURLField(required=True)
    ingredients = RecipeIngredientSerializer(many=True)
    steps = StepSerializer(many=True)
    author = serializers.StringRelatedField()

    class Meta:
        model = Recipe
        fields = (
            'recipe_name',
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
                ingredient=Ingredient.objects.get_or_create(
                    ingredient_name=ingredient_dict['ingredient']
                )[0],
                unit=ingredient_dict["unit"],
                amount=ingredient_dict["amount"],
            ) for ingredient_dict in ingredients_list
        ]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe_obj.ingredients.set(recipe_ingredients)

        # create steps
        steps_in_recipe = [
            RecipeStep(
                step_text=step_dict['step_text'],
                recipe=recipe_obj,
                image=step_dict.get('image', None)
            ) for step_dict in steps_list
        ]

        RecipeStep.objects.bulk_create(steps_in_recipe)
        recipe_obj.steps.set(steps_in_recipe)

        return recipe_obj

    def update(self, instance, validated_data):
        ingredients_list = validated_data.pop('ingredients')
        steps_list = validated_data.pop('steps')

        instance.recipe_name = validated_data.get('recipe_name')
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
                ingredient=Ingredient.objects.get_or_create(
                    ingredient_name=ingredient_dict['ingredient']
                )[0],
                unit=ingredient_dict["unit"],
                amount=ingredient_dict["amount"],
            ) for ingredient_dict in ingredients_list
        ]

        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        instance.ingredients.set(recipe_ingredients)

        # create steps
        steps_in_recipe = [
            RecipeStep(
                step_text=step_dict['step_text'],
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
        fields = ('comment_text', 'user', 'time_created')
