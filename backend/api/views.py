from datetime import datetime

from api.utils import download_recipe
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.filter(pk=pk).first()

        if request.method == 'POST':
            if not recipe:
                return Response('Рецепт не найден.',
                                status=status.HTTP_400_BAD_REQUEST)
            cart_instance, created = ShoppingCart.objects.get_or_create(
                customer=request.user, recipe=recipe)

            if created:
                serializer = ShoppingCartSerializer(
                    cart_instance, context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response('Рецепт уже в корзине.',
                                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if not recipe:
                return Response('Рецепт не найден.',
                                status=status.HTTP_404_NOT_FOUND)
            try:
                cart_instance = ShoppingCart.objects.get(
                    customer=request.user, recipe=recipe)
                cart_instance.delete()
                return Response('Рецепт удален из корзины.',
                                status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response('Рецепт не найден в корзине.',
                                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = Recipe.objects.filter(pk=pk).first()

        if request.method == 'POST':
            if not recipe:
                return Response(
                    'Попытка добавить несуществующий рецепт в избранное.',
                    status=status.HTTP_400_BAD_REQUEST)

            if not Favorite.objects.filter(customer=request.user,
                                           recipe=recipe).exists():
                instance = Favorite.objects.create(
                    customer=request.user, recipe=recipe)
                serializer = FavoriteSerializer(
                    instance, context={'request': request})
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response('Рецепт уже в избранном.',
                                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if not recipe:
                return Response('Рецепт не найден.',
                                status=status.HTTP_404_NOT_FOUND)

            cart_instance = Favorite.objects.filter(
                customer=request.user, recipe=recipe).exists()

            if cart_instance:
                Favorite.objects.get(recipe=recipe).delete()

                return Response('Рецепт удален из избранного.',
                                status=status.HTTP_204_NO_CONTENT)
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
