from django.shortcuts import render, get_object_or_404

from clones.forms import CloneSearchForm
from clones.models import Clone
from utils.pagination import get_paginated


CLONES_PER_PAGE = 20


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

    display_clones = get_paginated(request, clones, CLONES_PER_PAGE)

    context = {
        'clones': clones,
        'display_clones': display_clones,
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
