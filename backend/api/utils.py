from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Sum

from recipes.models import RecipeIngredient
from users.models import Follow

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
