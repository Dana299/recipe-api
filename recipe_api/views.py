from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Comment, Ingredient, Recipe, RecipeIngredient, RecipeStep
from .serializers import (CommentSerializer, RecipeDetailedSerializer,
                          RecipeListSerializer)


class RecipeViewSet(viewsets.ViewSet):
    """
    ViewSet for listing or retrieving recipes
    """
    def list(self, request):
        queryset = Recipe.objects.filter(status=Recipe.Status.PUBLISHED)
        serializer = RecipeListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Recipe.objects.filter(status=Recipe.Status.PUBLISHED)
        instance = get_object_or_404(queryset, pk=pk)
        serializer = RecipeDetailedSerializer(instance)
        return Response(serializer.data)


class CommentsViewSet(viewsets.ViewSet):
    """
    ViewSet for listing or creating comments on certain recipe
    """
    def list(self, request, pk=None):
        queryset = Comment.objects.filter(recipe=pk)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self):
        pass

