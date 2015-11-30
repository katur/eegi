from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_paginated(request, items, items_per_page):
    paginator = Paginator(items, items_per_page)

    page = request.GET.get('page')

    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)
