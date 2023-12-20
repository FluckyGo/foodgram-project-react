import os
import requests
from rest_framework import status
from rest_framework.response import Response
from django.utils.text import slugify
from fpdf import FPDF

from recipes.models import ShoppingCart, RecipeIngredient
from foodgram import settings

font_url = 'https://disk.yandex.ru/d/ml5YeIGjanUzSA'


def download_font(url=''):
    try:
        response = requests.get(url=url)

        with open('Roboto.ttf', 'wb') as file:
            file.write(response.content)
    except Exception as _ex:
        return ('Oopss... Check Url pls', _ex)


def download_recipe(self, request):
    user = request.user
    shopping_cart_items = ShoppingCart.objects.filter(customer=user)

    if not shopping_cart_items.exists():
        return None

    pdf = FPDF()
    pdf.add_page()

    font_path = download_font(url=font_url)

    pdf.add_font('Roboto', '', 'backend/Roboto.ttf')
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

    return pdf_path
