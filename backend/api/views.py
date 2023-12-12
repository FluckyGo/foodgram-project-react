from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import get_user_model
from .serializers import FollowSerializer, TagSerializer, IngredientSerializer, RecipeSerializer
from recipes.models import Tag, Recipe, Ingredient

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    ...
    # queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer


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
