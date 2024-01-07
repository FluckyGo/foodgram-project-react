from datetime import datetime

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewset
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow
from .utils import download_recipe, add_to_list, delete_from_list
from .filters import IngredientFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrIsAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          CustomUserReadSerializer, FollowSerializer,
                          FollowReadSerializer)
from .constants import (SHOPPING_CART_FAVORITE_SUCCESS_MESSAGE,
                        SHOPPING_CART_NOT_FOUND_MESSAGE,
                        SHOPPING_CART_BAD_REQUEST_MESSAGE,
                        FAVORITE_NOT_FOUND_MESSAGE,
                        FAVORITE_BAD_REQUEST_MESSAGE,
                        SUBSCRIBE_BAD_REQUEST_MESSAGE,
                        SUBSCRIBE_NOT_FOUND_MESSAGE, SUBSCRIBE_SUCCESS_MESSAGE)

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

        return add_to_list(
            ShoppingCartSerializer,
            ShoppingCart,
            data,
            request
        )

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        return delete_from_list(
            Recipe,
            ShoppingCart,
            request,
            pk,
            SHOPPING_CART_FAVORITE_SUCCESS_MESSAGE,
            SHOPPING_CART_NOT_FOUND_MESSAGE,
            SHOPPING_CART_BAD_REQUEST_MESSAGE
        )

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

        return add_to_list(
            FavoriteSerializer,
            Favorite,
            data,
            request
        )

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        return delete_from_list(
            Recipe,
            Favorite,
            request,
            pk,
            SHOPPING_CART_FAVORITE_SUCCESS_MESSAGE,
            FAVORITE_NOT_FOUND_MESSAGE,
            FAVORITE_BAD_REQUEST_MESSAGE
        )

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):

        txt_content = download_recipe(self, request)

        if txt_content is None:
            return Response('Корзина пуста.', status=status.HTTP_200_OK)

        date = datetime.now().strftime('%Y%m%d_%H%M%S')

        txt_filename = (f'shopping_cart_'
                        f'{slugify(request.user.username)}_{date}.txt')

        response = HttpResponse(
            txt_content, content_type='text/plain')
        response['Content-Disposition'] = (
            f'attachment; filename="{txt_filename}"')

        return response


class UserViewSet(DjoserUserViewset):
    """ Вью пользователя и управления подписками. """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = FoodgramPagination
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserReadSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(methods=['get'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        """ Получение подписок пользователя. """
        subscriptions = Follow.objects.filter(user=self.request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowReadSerializer(page,
                                          many=True,
                                          context={'request': self.request}
                                          )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id=None):
        ...

    @subscribe.mapping.post
    def add_to_subscribers(self, request, pk=None):
        following = get_object_or_404(User, pk=pk)

        data = {
            'user': request.user.id,
            'following': following.id,
        }

        return add_to_list(
            FollowSerializer,
            Follow,
            data,
            request
        )

    @subscribe.mapping.delete
    def delete_from_subscribers(self, request, pk=None):

        return delete_from_list(
            User,
            Follow,
            request,
            pk,
            SUBSCRIBE_SUCCESS_MESSAGE,
            SUBSCRIBE_NOT_FOUND_MESSAGE,
            SUBSCRIBE_BAD_REQUEST_MESSAGE
        )
