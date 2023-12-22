from rest_framework.pagination import LimitOffsetPagination


class FoodgramPagination(LimitOffsetPagination):
    """ Пагинация для проекта Фудграм. """
    default_limit = 6
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 30
