from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Comment, Ingredient, Recipe, RecipeIngredient, RecipeStep
from .pagination import CustomPagination
from .serializers import (CommentSerializer, RecipeDetailedSerializer,
                          RecipeListSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing or retrieving recipes
    """
    queryset = Recipe.objects.select_related('author').filter(status=Recipe.Status.PUBLISHED)
    serializer_class = RecipeListSerializer
    pagination_class = CustomPagination

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = RecipeListSerializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data)
        else:
            serializer = RecipeListSerializer(queryset, many=True)
            return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Recipe.objects.filter(status=Recipe.Status.PUBLISHED)
        instance = get_object_or_404(queryset, pk=pk)
        serializer = RecipeDetailedSerializer(instance)
        return Response(serializer.data)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing or creating comments on certain recipe
    """
    queryset = Comment.objects.all().select_related('user')
    pagination_class = CustomPagination
    serializer_class = CommentSerializer

    def list(self, request, pk=None):
        queryset = self.get_queryset().filter(recipe=pk)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = CommentSerializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data)
        else:
            serializer = CommentSerializer(queryset, many=True)
            return Response(serializer.data)

    def create(self):
        pass

