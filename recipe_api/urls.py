from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, CommentsViewSet

app_name = 'recipe_api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')

# router for comments
comment_router = DefaultRouter()
comment_router.register(r'feedbacks', CommentsViewSet, basename='feedbacks')


urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:pk>/', include(comment_router.urls)),
]

