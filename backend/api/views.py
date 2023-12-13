from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import get_user_model
from .serializers import TagSerializer, IngredientSerializer, RecipeReadSerializer, RecipeWriteSerializer
from recipes.models import Tag, Recipe, Ingredient
from .pagination import FoodgramPagination

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (permissions.AllowAny,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = FoodgramPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        ...

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        ...

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        ...
