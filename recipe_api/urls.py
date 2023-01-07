from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CommentsViewSet, ImageViewSet, RecipeViewSet

app_name = 'recipe_api'

# router for recipes
recipe_router = SimpleRouter()
recipe_router.register(r'recipes', RecipeViewSet, basename='recipes')

# router for comments
comment_router = SimpleRouter()
comment_router.register(r'feedbacks', CommentsViewSet, basename='feedbacks')

# router for pictures
image_router = SimpleRouter()
image_router.register(r'upload-image', ImageViewSet, basename='upload-image')

urlpatterns = [
    path('', include(recipe_router.urls)),
    path('recipes/<int:pk>/', include(comment_router.urls)),
    path('', include(image_router.urls)),
]
