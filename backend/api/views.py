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
from .utils import download_recipe
from .filters import IngredientFilter, RecipeFilter
from .pagination import FoodgramPagination
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrIsAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          CustomUserReadSerializer, FollowSerializer,
                          FollowReadSerializer)
from .constants import (SHOPPING_CART_FAVORITE_SUCCESS_MESSAGE,
                        SHOPPING_CART_BAD_REQUEST_MESSAGE,
                        FAVORITE_BAD_REQUEST_MESSAGE,
                        SUBSCRIBE_BAD_REQUEST_MESSAGE,
                        SUBSCRIBE_SUCCESS_MESSAGE)

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

    @staticmethod
    def add_to_list(serializer_class, data, request):
        serializer = serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_from_list(item_model_class, instance_model_class, request,
                         pk=None,
                         success_message='',
                         bad_request_message=''):

        item = get_object_or_404(item_model_class, pk=pk)

        delete_cnt, _ = instance_model_class.objects.filter(
            customer=request.user, recipe=item).delete()

        if delete_cnt:
            return Response(success_message, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(bad_request_message,
                            status=status.HTTP_400_BAD_REQUEST)

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

        return self.add_to_list(
            ShoppingCartSerializer,
            data,
            request
        )

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        return self.delete_from_list(
            Recipe,
            ShoppingCart,
            request,
            pk,
            SHOPPING_CART_FAVORITE_SUCCESS_MESSAGE,
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

        return self.add_to_list(
            FavoriteSerializer,
            data,
            request
        )

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        return self.delete_from_list(
            Recipe,
            Favorite,
            request,
            pk,
            SHOPPING_CART_FAVORITE_SUCCESS_MESSAGE,
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
        subscriptions = Follow.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowReadSerializer(page,
                                          many=True,
                                          context={'request': request}
                                          )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, id=None):
        ...

    @subscribe.mapping.post
    def add_to_subscribers(self, request, pk=None):
        """ Функция добавляет пользователя в подписки. """

        following = get_object_or_404(User, pk=pk)

        data = {
            'user': request.user.id,
            'following': following.id,
        }

        serializer = FollowSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_from_subscribers(self, request, pk=None):
        """ Функция удаляет пользователя из подписок. """

        item = get_object_or_404(User, pk=pk)

        delete_cnt, _ = Follow.objects.filter(
            user=request.user, following=item).delete()

        if delete_cnt:
            return Response(SUBSCRIBE_SUCCESS_MESSAGE,
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(SUBSCRIBE_BAD_REQUEST_MESSAGE,
                            status=status.HTTP_400_BAD_REQUEST)
