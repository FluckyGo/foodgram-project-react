from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import get_user_model
from .serializers import FollowSerializer, TagSerializer, IngredientSerializer, RecipeSerializer
from recipes.models import Tag, Recipe, Ingredient

User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):

    serializer_class = FollowSerializer
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('user', 'following')
    search_fields = ('user__username', 'following__username')
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.follower.all()

    def perform_create(self, serializer):

        following_user = get_object_or_404(
            User, username=self.request.data.get('following'))

        serializer.save(
            user=self.request.user,
            following=following_user
        )
