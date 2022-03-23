from urllib import request

from django.core.paginator import Paginator
from yatube.settings import PAGINOR_COUNT_PAGE


def paginator(request: request, post_list: dict) -> Paginator:
    """Возращает готовый page_obj для пагинации """
    paginator = Paginator(post_list, PAGINOR_COUNT_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
