from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from colorfield.fields import ColorField

from api.constants import MAX_MODEL_FIELD_LENGTH

User = get_user_model()


class Tag(models.Model):
    """ Модель тегов. """

    name = models.CharField('Наименование тега',
                            max_length=MAX_MODEL_FIELD_LENGTH, unique=True)
    color = ColorField('Цвет тега', max_length=7, unique=True)
    slug = models.SlugField(
        'Слаг тега', max_length=MAX_MODEL_FIELD_LENGTH, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингридиентов. """
    name = models.CharField(
        'Название ингридиента',
        max_length=MAX_MODEL_FIELD_LENGTH,
        db_index=True
    )

    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=MAX_MODEL_FIELD_LENGTH
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient')
        ]

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """ Модель рецептов. """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор рецепта')

    name = models.CharField(
        'Название рецепта', max_length=MAX_MODEL_FIELD_LENGTH, db_index=True)
    image = models.ImageField('Изображение блюда', upload_to='media/')
    text = models.TextField('Описание рецепта')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    tags = models.ManyToManyField(Tag, verbose_name='Тег')

    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингридиенты', through='RecipeIngredient')

    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки',
        validators=[
            MinValueValidator(
                1,
                'Время готовки должно быть больше 0.'),
            MaxValueValidator(
                32767,
                'Проще купить, чем столько готовить.')
        ])

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        default_related_name = 'recipe'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_recipes')
        ]

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """ Ингридиенты для использования в рецепте. """
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        related_name='recipe_ingredients')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент рецепта')
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=[
            MinValueValidator(
                1,
                'Количество ингридиента должно быть больше 0.'),
            MaxValueValidator(
                999999,
                'Куда тебе столько?')
        ])

    class Meta:
        verbose_name = 'Ингридиент для рецепта'
        verbose_name_plural = 'Ингридиенты для рецепта'
        ordering = ('recipe',)

    def __str__(self) -> str:
        return f'{self.ingredient_name} -- {self.amount}'

    def ingredient_name(self):
        return f'{self.ingredient} - {self.amount}'


class ShoppingCart(models.Model):
    """ Модель списка покупок. """
    customer = models.ForeignKey(
        User,
        related_name='user_shopping_cart',
        verbose_name='Покупатель',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт блюда',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        ordering = ('customer',)

    def __str__(self) -> str:
        return self.recipe


class Favorite(models.Model):
    """ Модель избранного. """
    customer = models.ForeignKey(
        User,
        related_name='user_favorites',
        verbose_name='Покупатель',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite',
        verbose_name='Рецепт блюда',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Любимые рецепты'
        verbose_name_plural = 'Любимые рецепты'
        ordering = ('customer',)

    def __str__(self) -> str:
        return self.recipe
