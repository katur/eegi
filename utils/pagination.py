"""Utility module for help paginating results."""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_paginated(request, items, items_per_page):
    """
    Paginate items according to items_per_page, and return the page
    specified in request.GET.
    """
    paginator = Paginator(items, items_per_page)

    page = request.GET.get('page')

    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
