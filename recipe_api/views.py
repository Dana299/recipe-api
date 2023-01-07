from rest_framework import mixins, viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Comment, Image, Recipe
from .pagination import CustomPagination
from .serializers import (CommentSerializer, ImagePostSerializer,
                          RecipeDetailedSerializer, RecipeListSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, updating and creating recipes
    """
    queryset = Recipe.objects.select_related('author').filter(status=Recipe.Status.PUBLISHED)
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'head', 'put', 'delete']

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            return RecipeListSerializer()
        else:
            return RecipeDetailedSerializer()


class CommentsViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet for listing and creating comments on certain recipe
    """
    queryset = Comment.objects.all().select_related('user')
    pagination_class = CustomPagination
    serializer_class = CommentSerializer


class ImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Viewset for uploading pictures
    """
    queryset = Image.objects.all()
    serializer_class = ImagePostSerializer
    parser_classes = (MultiPartParser, FormParser)