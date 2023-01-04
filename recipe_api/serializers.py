import re

from rest_framework import serializers

from .models import (Comment, Image, Ingredient, Recipe, RecipeIngredient,
                     RecipeStep)


class SlugRelatedGetOrCreateField(serializers.SlugRelatedField):
    """
    Custom SlugRelatedField to create an object
    if it doesn't exist in the database
    """
    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            obj, created = queryset.get_or_create(**{self.slug_field: data})
            return obj
        except (TypeError, ValueError):
            self.fail("invalid")


class ImagePostSerializer(serializers.ModelSerializer):
    """
    Serializer for images apart
    """
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = ('image',)


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for images in recipes
    """
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Image
        fields = ('image',)

    def to_internal_value(self, data):
        filename = re.search(r'[^\/]*\.jpg', data['image']).group(0)
        obj = Image.objects.get(image=filename)
        return obj


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Serializer for a list of recipes on home page
    """

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
    image = ImageSerializer()

    class Meta:
        model = RecipeStep
        fields = ('step_text', 'image',)

    def create(self, validated_data):
        step = RecipeStep.objects.create(**validated_data)
        return step


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for ingredients in recipes
    """
    ingredient = SlugRelatedGetOrCreateField(
        queryset=Ingredient.objects.all(),
        slug_field='ingredient_name'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'unit', 'amount')

    def create(self, validated_data):
        ingredient, created = Ingredient.objects.get_or_create(
                **validated_data
            )
        return ingredient


class RecipeDetailedSerializer(serializers.ModelSerializer):
    """
    Serializer for a certain recipe - more fields included
    """
    main_picture = ImageSerializer()
    ingredients = RecipeIngredientSerializer(many=True)
    steps = StepSerializer(many=True)

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
        # pop ingredients and steps
        ingredients_list = validated_data.pop('ingredients', [])
        steps_list = validated_data.pop('steps', [])
        # create recipe instance
        recipe_obj = Recipe.objects.create(**validated_data)
        # create ingredients and connections RecipeIngredients
        for ingredient_dict in ingredients_list:
            ingredient_name = ingredient_dict['ingredient']
            ingredient, created = Ingredient.objects.get_or_create(
                ingredient_name=ingredient_name
            )
            recipe_ing_obj = RecipeIngredient.objects.create(
                recipe=recipe_obj,
                ingredient=ingredient,
                unit=ingredient_dict["unit"],
                amount=ingredient_dict["amount"],
            )

            recipe_obj.ingredients.add(recipe_ing_obj)

        # create steps
        for step_dict in steps_list:
            print(step_dict)
            step_text = step_dict['step_text']
            image_instance = step_dict['image']
            step = RecipeStep.objects.create(
                step_text=step_text,
                recipe=recipe_obj,
                image=image_instance
            )

            recipe_obj.steps.add(step)

        return recipe_obj


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments
    """
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ('comment_text', 'user', 'time_created')
