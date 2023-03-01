from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from utils.image_converter import JpegConverter

from .models import Comment, Image, Recipe
from .pagination import CustomPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (CommentSerializer, ImagePostSerializer,
                          RecipeDetailedSerializer, RecipeListSerializer)

comment_text_param = openapi.Parameter(
    'text',
    openapi.IN_BODY,
    type=openapi.TYPE_STRING
)
user_response = openapi.Response('response description', CommentSerializer)
list_response = openapi.Response('resp', RecipeDetailedSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, updating and creating recipes
    """
    queryset = Recipe.objects.select_related('author').filter(status=Recipe.Status.PUBLISHED)
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'head', 'put', 'delete']
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly, )

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return RecipeListSerializer
        else:
            return RecipeDetailedSerializer


class CommentsViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """
    ViewSet for listing and creating comments on certain recipe
    """
    pagination_class = CustomPagination
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return Comment.objects.filter(recipe=recipe).select_related('user')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"recipe_pk": self.kwargs['pk']})
        return context

    @swagger_auto_schema(
        operation_description="Create comment on certain recipe",
        request_body=openapi.Schema(
            title='Comment',
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    min_length=1,
                    max_length=1000,
                ),
            },
        ),
        responses={201: user_response}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Viewset for uploading pictures
    """
    queryset = Image.objects.all()
    serializer_class = ImagePostSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        validated_image = serializer.validated_data['image']

        # Convert image to JPEG format
        converted_image = JpegConverter.convert(validated_image)

        serializer.save(image=converted_image)