import os

from django.utils.text import slugify
from foodgram import settings
from recipes.models import Ingredient, RecipeIngredient, ShoppingCart


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
