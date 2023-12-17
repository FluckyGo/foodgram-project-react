import os
from rest_framework import viewsets, mixins, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.text import slugify
from django.forms.models import model_to_dict
from fpdf import FPDF

from foodgram import settings

from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, FavoriteSerializer)
from .pagination import FoodgramPagination
from .filters import RecipeFilter, IngredientFilter
from recipes.models import RecipeIngredient, Tag, Recipe, Ingredient, ShoppingCart, Favorite

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter, )
    permission_classes = (permissions.AllowAny,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = FoodgramPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    # filterset_fields = ('author', 'tags',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, pk=None):

        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':

            if not ShoppingCart.objects.filter(customer=request.user,
                                               recipe=recipe).exists():
                instance = ShoppingCart.objects.create(
                    customer=request.user, recipe=recipe)
                serializer = ShoppingCartSerializer(
                    instance, context={'request': request})
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
            else:
                return Response('Рецепт уже в корине.',
                                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':

            cart_instance = ShoppingCart.objects.filter(
                customer=request.user, recipe=recipe).exists()

            if cart_instance:
                ShoppingCart.objects.get(recipe=recipe).delete()

                return Response('Рецепт удален из корзины.',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Вы пытаетесь удалить рецепт,'
                            ' которого нет в корзине!')

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':

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

            cart_instance = Favorite.objects.filter(
                customer=request.user, recipe=recipe).exists()

            if cart_instance:
                Favorite.objects.get(recipe=recipe).delete()

                return Response('Рецепт удален из избранного.',
                                status=status.HTTP_204_NO_CONTENT)
            return Response('Вы пытаетесь удалить рецепт,'
                            ' которого нет в избранном!')

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_items = ShoppingCart.objects.filter(customer=user)

        if not shopping_cart_items.exists():
            return Response('Корзина пуста.', status=status.HTTP_200_OK)

        pdf = FPDF()
        pdf.add_page()
        font_path = 'backend/foodgram/Roboto-Light.ttf'
        pdf.add_font('Roboto', '', font_path)
        pdf.set_font('Roboto', size=12)

        ingredients_dict = {}

        for item in shopping_cart_items:
            recipe = item.recipe
            recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)

            for recipe_ingredient in recipe_ingredients:
                ingredient = recipe_ingredient.ingredient
                ingredient_name = ingredient.name
                amount = recipe_ingredient.amount

                if ingredient_name in ingredients_dict:
                    ingredients_dict[ingredient_name] += amount
                else:
                    ingredients_dict[ingredient_name] = amount

        for ingredient_name, amount in ingredients_dict.items():
            pdf.cell(
                200, 10, txt=f'{ingredient_name} ({amount} {recipe_ingredient.ingredient.measurement_unit})', ln=True, align='L')

        pdf_filename = f"shopping_cart_{slugify(user.username)}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
        pdf.output(pdf_path)

        with open(pdf_path, 'rb') as file:
            response = HttpResponse(
                file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'

        os.remove(pdf_path)

        return response
