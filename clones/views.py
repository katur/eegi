from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from clones.models import Clone


def clones(request):
    """
    Render the page to see RNAi clones.
    """
    clones = Clone.objects.all()
    paginator = Paginator(clones, 100)
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
