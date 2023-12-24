from rest_framework.pagination import PageNumberPagination


class FoodgramPagination(PageNumberPagination):
    """ Пагинация для проекта Фудграм. """
    page_size_query_param = 'limit'
    page_size = 6
