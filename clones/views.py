from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404

from clones.forms import CloneSearchForm
from clones.models import Clone


CLONES_PER_PAGE = 100


def clones(request):
    """Render the page listing all RNAi clones."""
    if 'clone_query' in request.GET:
        form = CloneSearchForm(request.GET)

        if form.is_valid():
            data = form.cleaned_data
            clones = data['clone_query']
        else:
            clones = []

    else:
        form = CloneSearchForm()
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
        'form': form,
    }

    return render(request, 'clones.html', context)


def clone(request, id):
    """Render the page to view a single RNAi clone."""
    clone = get_object_or_404(Clone, pk=id)

    context = {
        'clone': clone,
    }

    return render(request, 'clone.html', context)
