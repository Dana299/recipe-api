from rest_framework import serializers

from .models import Comment, Ingredient, Recipe, RecipeIngredient, RecipeStep


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
    class Meta:
        model = RecipeStep
        fields = ('step_text', 'image_url',)


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
            'ingredients',
            'steps',
        )

    def validate(self, data):
        ingredients = data['ingredients']
        if len(ingredients) == 0:
            raise serializers.ValidationError('Recipe must have at least one ingredient')
        return data

    def create(self, validated_data):
        # pop ingredients
        ingredients_list = validated_data.pop('ingredients', [])
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

        return recipe_obj


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comments
    """
    user = serializers.StringRelatedField()
    class Meta:
        model = Comment
        fields = ('comment_text', 'user', 'time_created')