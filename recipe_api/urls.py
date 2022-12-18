from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CommentsViewSet, RecipeDetailedViewSet, RecipeListViewSet

app_name = 'recipe_api'

router = SimpleRouter()
router.register(r'recipes', RecipeListViewSet, basename='recipes')

# router for comments
comment_router = SimpleRouter()
comment_router.register(r'feedbacks', CommentsViewSet, basename='feedbacks')

recipe_create = RecipeDetailedViewSet.as_view({
    'post': 'create',
})

recipe_get = RecipeDetailedViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
})

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:pk>/', include(comment_router.urls)),
    path('recipes/new/', recipe_create),
    path('recipes/<int:pk>/', recipe_get),
]

