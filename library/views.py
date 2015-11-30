from django.shortcuts import render, get_object_or_404

from library.models import LibraryPlate
from library.helpers.queries import get_screening_plates
from utils.pagination import get_paginated


PLATES_PER_PAGE = 100


def library_plates(request):
    """Render the page listing all library plates."""
    screen_stage = request.GET.get('screen_stage')
    library_plates = get_screening_plates(screen_stage=screen_stage)
    display_plates = get_paginated(request, library_plates,
                                   PLATES_PER_PAGE)
    context = {
        'library_plates': library_plates,
        'display_plates': display_plates,
    }

    return render(request, 'library_plates.html', context)


def library_plate(request, pk):
    """Render the page showing the contents of a single library plate."""
    library_plate = get_object_or_404(LibraryPlate, pk=pk)
    library_stocks = library_plate.get_all_stocks()

    context = {
        'library_plate': library_plate,
        'library_stocks': library_stocks,
    }

    return render(request, 'library_plate.html', context)
