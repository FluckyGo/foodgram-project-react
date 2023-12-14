from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from .serializers import CustomUserReadSerializer, CustomUserWriteSerializer
from followers.models import Follow
from followers.serializers import FollowSerializer
from api.pagination import FoodgramPagination


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = FoodgramPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserReadSerializer
        return CustomUserWriteSerializer

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        ''' Получение профиля текущего пользователя. '''
        instance = self.request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['post'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,)
            )
    def set_password(self, request):
        ''' Смена пароля текущего пользователя. '''
        new_password = self.request.data.get('new_password')

        request.user.password = make_password(new_password)
        request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

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
