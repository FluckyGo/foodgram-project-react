from datetime import datetime

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from api.utils import download_recipe
from .filters import IngredientFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrIsAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUserOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter, )
    permission_classes = (IsAdminUserOrReadOnly,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = FoodgramPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsOwnerOrIsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        ...

    @shopping_cart.mapping.post
    def add_to_shopping_cart(self, request, pk=None):

        data = {
            'customer': request.user.id,
            'recipe': pk,
        }

        serializer = ShoppingCartSerializer(
            data=data, context={'request': request, 'recipe_pk': pk})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.filter(pk=pk).first()

        if not recipe:
            return Response('Рецепт не найден.',
                            status=status.HTTP_404_NOT_FOUND)

        delete_cnt, _ = ShoppingCart.objects.filter(
            customer=request.user, recipe=recipe).delete()

        if delete_cnt:
            return Response('Рецепт удален из корзины.',
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return Response('Рецепт не найден в корзине.',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        ...

    @favorite.mapping.post
    def add_to_favorite(self, request, pk=None):

        data = {
            'customer': request.user.id,
            'recipe': pk,
        }

        serializer = FavoriteSerializer(
            data=data, context={'request': request, 'recipe_pk': pk})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        recipe = Recipe.objects.filter(pk=pk).first()

        if not recipe:
            return Response('Рецепт не найден.',
                            status=status.HTTP_404_NOT_FOUND)

        delete_cnt, _ = Favorite.objects.filter(
            customer=request.user, recipe=recipe).delete()

        if delete_cnt:
            return Response('Рецепт удален из избранного.',
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return Response('Вы пытаетесь удалить рецепт,'
                            ' которого нет в избранном!',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user

        txt_content = download_recipe(self, request)

        if txt_content is None:
            return Response('Корзина пуста.', status=status.HTTP_200_OK)

        date = datetime.now().strftime('%Y%m%d_%H%M%S')

        txt_filename = f'shopping_cart_{slugify(user.username)}_{date}.txt'

        response = HttpResponse(
            txt_content, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{txt_filename}"')

        return response
