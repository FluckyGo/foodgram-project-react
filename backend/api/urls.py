from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, TagViewSet, IngredientViewSet
from users.views import UserViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
