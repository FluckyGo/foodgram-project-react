from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import FollowSerializer


User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):
    """ Вью для модели подписок. """

    serializer_class = FollowSerializer
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
