from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from clones.models import Clone


CLONES_PER_PAGE = 100


def clones(request):
    """Render the page listing all RNAi clones."""
    clones = Clone.objects.all()
    paginator = Paginator(clones, CLONES_PER_PAGE)
    page = request.GET.get('page')

    try:
        paginated = paginator.page(page)
    except PageNotAnInteger:
        paginated = paginator.page(1)
    except EmptyPage:
        paginated = paginator.page(paginator.num_pages)

    context = {
        'clones': clones,
        'paginated': paginated,
    }

    return render(request, 'clones.html', context)
