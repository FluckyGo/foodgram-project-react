PAGINATION_PAGE_SIZE = 6

USER = 'user'
ADMIN = 'admin'

USER_ROLES = [
    (USER, 'user'),
    (ADMIN, 'admin'),
]

DEFAULT_FOLLOW_RECIPE_LIMIT = 4
MAX_MODEL_FIELD_LENGTH = 200
MAX_USER_MODEL_FIELD_LENGTH = 150

USERNAME_REGEX = r'^[\w.@+-]+$'

SHOPPING_CART_FAVORITE_SUCCESS_MESSAGE = 'Рецепт не найден.'
SHOPPING_CART_NOT_FOUND_MESSAGE = 'Рецепт удален из корзины.'
SHOPPING_CART_BAD_REQUEST_MESSAGE = 'Рецепт не найден в корзине.'


FAVORITE_NOT_FOUND_MESSAGE = 'Рецепт удален из избранного.'
FAVORITE_BAD_REQUEST_MESSAGE = (
    'Вы пытаетесь удалить рецепт,'
    ' которого нет в избранном!')


SUBSCRIBE_SUCCESS_MESSAGE = 'Подписка отменена.'
SUBSCRIBE_NOT_FOUND_MESSAGE = 'Подписка не найдена.'
SUBSCRIBE_BAD_REQUEST_MESSAGE = (
    'Вы пытаетесь отписаться от себя или от'
    ' пользователя на которого ещё не подписаны.')
