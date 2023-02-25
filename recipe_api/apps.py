from django.apps import AppConfig


class RecipeApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recipe_api"

    def ready(self):
        from recipe_api import signals
