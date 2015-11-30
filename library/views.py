from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from library.models import LibraryPlate
from utils.pagination import get_paginated


PLATES_PER_PAGE = 100


def library_plates(request):
    """Render the page listing all library plates."""
    screen_stage = request.GET.get('screen_stage')
    if screen_stage:
        library_plates = LibraryPlate.objects.filter(
            Q(screen_stage=screen_stage) | Q(screen_stage=None))
    else:
        library_plates = LibraryPlate.objects.exclude(screen_stage=0)

    library_plates = sorted(library_plates)

    display_plates = get_paginated(request, library_plates, PLATES_PER_PAGE)

    context = {
        'library_plates': library_plates,
        'display_plates': display_plates,
    }

    return render(request, 'library_plates.html', context)


def library_plate(request, id):
    """Render the page showing the contents of a single library plate."""
    library_plate = get_object_or_404(LibraryPlate, pk=id)
    library_stocks = (library_plate.librarystock_set.all()
                      .select_related('intended_clone')
                      .order_by('well'))

    context = {
        'library_plate': library_plate,
        'library_stocks': library_stocks,
    }

    return render(request, 'library_plate.html', context)
