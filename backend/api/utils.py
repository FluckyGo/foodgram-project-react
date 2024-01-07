import os

from rest_framework.response import Response
from rest_framework import status
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from foodgram import settings
from recipes.models import Ingredient, RecipeIngredient, ShoppingCart
from users.models import Follow

User = get_user_model()


def download_recipe(self, request):
    """ Функция для скачивания списка покупок. """
    shopping_cart_count = 0
    user = request.user
    shopping_cart_items = ShoppingCart.objects.filter(customer=user)

    if not shopping_cart_items.exists():
        return None

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

    txt_content = ''
    for ingredient_name, amount in ingredients_dict.items():
        measurement_unit = Ingredient.objects.get(
            name=ingredient_name).measurement_unit
        txt_content += f'{ingredient_name.capitalize()} -- {amount} ' \
                       f'{measurement_unit}.\n'

    shopping_cart_count += 1

    txt_filename = f'shopping_cart_{slugify(shopping_cart_count)}.txt'
    txt_path = os.path.join(settings.MEDIA_ROOT, txt_filename)

    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write('Список ингредиентов для покупки:\n\n')
        txt_file.write(txt_content)

    return txt_content


def add_to_list(serializer_class, model_class, data, request):
    serializer = serializer_class(data=data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_from_list(item_model_class, instance_model_class, request,
                     pk=None,
                     success_message='',
                     not_found_message='',
                     bad_request_message=''):
    item = item_model_class.objects.filter(pk=pk).first()

    if not item:
        return Response(not_found_message, status=status.HTTP_404_NOT_FOUND)

    if item_model_class == User and instance_model_class == Follow:
        delete_cnt, _ = instance_model_class.objects.filter(
            user=request.user, following=item).delete()
    else:
        delete_cnt, _ = instance_model_class.objects.filter(
            customer=request.user, recipe=item).delete()

    if delete_cnt:
        return Response(success_message, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response(bad_request_message,
                        status=status.HTTP_400_BAD_REQUEST)
