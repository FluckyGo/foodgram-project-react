from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as CustomUserViewset
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from followers.serializers import FollowSerializer
from followers.models import Follow
from api.pagination import FoodgramPagination
from .models import CustomUser
from .serializers import CustomUserReadSerializer, CustomUserWriteSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ Вью пользователя и управления подписками. """
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = FoodgramPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserReadSerializer
        return CustomUserWriteSerializer

    # def get_serializer_class(self):
    #     if self.action in ('list', 'retrieve'):
    #         return CustomUserReadSerializer
    #     return super().get_serializer_class()

    # def get_permissions(self):
    #     if self.action == 'me':
    #         return (permissions.IsAuthenticated(),)
    #     return super().get_permissions()

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """ Получение профиля текущего пользователя. """
        instance = self.request.user
        serializer = CustomUserReadSerializer(instance)
        return Response(serializer.data)

    @action(methods=['post'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,)
            )
    def set_password(self, request):
        """ Смена пароля текущего пользователя. """
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request})

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        if not check_password(current_password, request.user.password):
            return Response({'detail': 'Не верно указан текущий пароль.'},
                            status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()

        return Response({'detail': 'Пароль успешно изменен.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        """ Получение подписок пользователя. """
        subscriptions = Follow.objects.filter(user=self.request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(page, many=True, context={
                                      'request': self.request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, pk=None):

        following = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if following == self.request.user:
                return Response('Вы не можете подписаться на себя',
                                status=status.HTTP_400_BAD_REQUEST)

            if not Follow.objects.filter(user=self.request.user,
                                         following=following).exists():
                instance = Follow.objects.create(
                    user=request.user, following=following)
                serializer = FollowSerializer(
                    instance, context={'request': request})
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response('Вы уже подписаны',
                                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':

            follow_instance = Follow.objects.filter(
                user=request.user, following=following).exists()

            if follow_instance:
                Follow.objects.get(following=following).delete()

                return Response('Подписка отменена',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Вы пытаетесь отписаться от себя или'
                            ' от пользователя на которого ещё не подписаны!',
                            status=status.HTTP_400_BAD_REQUEST)
