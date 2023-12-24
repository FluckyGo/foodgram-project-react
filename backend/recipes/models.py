from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Tag(models.Model):
    """ Модель тегов. """
    ORANGE = '#FFA500'
    AQUA = '#00FFFF'
    INDIGO = '#4B0082'

    COLOR_SET = [
        (ORANGE, 'Оранжевый'),
        (AQUA, 'Бирюзовый'),
        (INDIGO, 'Синий'),
    ]

    name = models.CharField('Наименование тега', max_length=200, unique=True)
    color = models.CharField('Цвет тега', max_length=7,
                             choices=COLOR_SET, default=ORANGE, unique=True)
    slug = models.SlugField('Слаг тега', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """ Модель ингридиентов. """
    name = models.CharField(
        'Название ингридиента',
        max_length=200,
        db_index=True
    )

    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """ Модель рецептов. """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор рецепта')

    name = models.CharField('Название рецепта', max_length=200, db_index=True)
    image = models.ImageField('Изображение блюда', upload_to='media/')
    text = models.TextField('Описание рецепта')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    tags = models.ManyToManyField(Tag, verbose_name='Тег')

    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингридиенты', through='RecipeIngredient')

    cooking_time = models.PositiveSmallIntegerField('Время готовки')

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
    amount = models.PositiveSmallIntegerField('Количество ингредиента')

    class Meta:
        verbose_name = 'Ингридиент для рецепта'
        verbose_name_plural = 'Ингридиенты для рецепта'

        def __str__(self) -> str:
            return f'{self.ingredient.name} -- {self.amount}'


class ShoppingCart(models.Model):
    """ Модель списка покупок. """
    customer = models.ForeignKey(
        User, verbose_name='Покупатель', on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт блюда', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self) -> str:
        return self.recipe.name


class Favorite(models.Model):
    """ Модель избранного. """
    customer = models.ForeignKey(
        User, verbose_name='Покупатель', on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт блюда', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Любимые рецепты'
        verbose_name_plural = 'Любимые рецепты'

    def __str__(self) -> str:
        return self.recipe.name
