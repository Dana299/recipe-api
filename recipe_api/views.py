import json

from django.shortcuts import get_object_or_404, render
from rest_framework import mixins, status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import (Comment, Image, Ingredient, Recipe, RecipeIngredient,
                     RecipeStep)
from .pagination import CustomPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (CommentSerializer, ImageSerializer,
                          RecipeDetailedSerializer, RecipeListSerializer)


class RecipeListViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """
    ViewSet for listing recipes
    """
    queryset = Recipe.objects.select_related('author').filter(status=Recipe.Status.PUBLISHED)
    serializer_class = RecipeListSerializer
    pagination_class = CustomPagination

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


class RecipeDetailedViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            viewsets.GenericViewSet):
    """
    ViewSet for retrieving detailed recipe info,
    updating existing recipes and creating new recipe instance
    """
    queryset = Recipe.objects.filter(status=Recipe.Status.PUBLISHED)
    serializer_class = RecipeDetailedSerializer
    parser_classes = (MultiPartParser, FormParser, )
    permission_classes = (IsOwnerOrReadOnly, )

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = RecipeDetailedSerializer(instance)
        return Response(serializer.data)

    def create(self, request, format=None):
        serializer = self.get_serializer(request.data)
        # print(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        instance = get_object_or_404(Recipe.objects.all(), pk=pk)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentsViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
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

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Viewset for uploading pictures
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        image = models.Image.objects.create(image=file)
        return HttpResponse(json.dumps({'message': "Uploaded"}), status=200)