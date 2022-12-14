from rest_framework import serializers

from .models import Comment, Ingredient, Recipe, RecipeIngredient, RecipeStep


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Serializer for ingredients in recipes
    """
    ingredient = serializers.StringRelatedField()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'unit', 'amount')


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
            'main_picture',
        )


class StepSerializer(serializers.ModelSerializer):
    """
    Serializer for recipe steps
    """
    class Meta:
        model = RecipeStep
        fields = ('step_text', 'image_url',)


class RecipeDetailedSerializer(serializers.ModelSerializer):
    """
    Serializer for a certain recipe - more fields included
    """
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    steps = StepSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'recipe_name',
            'author',
            'category',
            'is_spicy',
            'is_vegetarian',
            'main_picture',
            'time_cooking',
            'time_preparing',
            'time_created',
            'ingredients',
            'steps',
        )


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments
    """
    user = serializers.StringRelatedField()
    class Meta:
        model = Comment
        fields = ('comment_text', 'user', 'time_created')