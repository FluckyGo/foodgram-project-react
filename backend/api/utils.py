from django.contrib.auth import get_user_model
from django.db.models import Sum

from recipes.models import RecipeIngredient

User = get_user_model()


def download_recipe(self, request):
    """ Функция для скачивания списка покупок. """

    ingredients_data = RecipeIngredient.objects.values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(total_ingredients=Sum('amount'))

    txt_content = 'Список ингредиентов для покупки:\n\n'

    for item in ingredients_data:
        ingredient_name = item.get('ingredient__name')
        measurement_unit = item.get('ingredient__measurement_unit')
        tolal_amount = item.get('total_ingredients')

        txt_content += (f'{ingredient_name.capitalize()} -- {tolal_amount}'
                        f' {measurement_unit}.\n')

    return txt_content
