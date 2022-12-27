from django.contrib import admin

from .models import Comment, Ingredient, Recipe, RecipeIngredient, RecipeStep


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user', 'time_created')


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'recipe_name',
        'author',
        'category',
        'get_no_ingredients',
        'time_created'
    )

    def get_no_ingredients(self, obj):
        no_ingredients = RecipeIngredient.objects.filter(recipe=obj.pk).count()
        return no_ingredients
    get_no_ingredients.short_description = "No of ingredients"


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RecipeIngredient._meta.get_fields()]


class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'image',)


admin.site.register(Comment, CommentAdmin)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(RecipeStep, RecipeStepAdmin)
