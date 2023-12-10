from rest_framework import viewsets
from rest_framework.permissions import (AllowAny)
from rest_framework.decorators import action
from .models import CustomUser
from .serializers import CustomUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = CustomUserSerializer

    @action(methods=['get'], detail=True)
    def me(self, request):
        ...

    @action(methods=['post'], detail=True)
    def set_password(self, request):
        ...
