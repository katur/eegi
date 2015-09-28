from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404

from experiments.models import Experiment
from library.models import LibraryPlate, LibraryWell


PLATES_PER_PAGE = 100


def library_plates(request):
    """Render the page listing all library plates."""
    screen_stage = request.GET.get('screen_stage')
    if screen_stage:
        plate_pks = (Experiment.objects
                     .filter(screen_stage=screen_stage)
                     .order_by('library_plate')
                     .values_list('library_plate', flat=True)
                     .distinct())
        library_plates = sorted(LibraryPlate.objects.filter(
            pk__in=plate_pks))
    else:
        library_plates = sorted(LibraryPlate.objects.filter(
            screen_stage__gte=1))

    paginator = Paginator(library_plates, PLATES_PER_PAGE)
    page = request.GET.get('page')

    try:
        display_plates = paginator.page(page)
    except PageNotAnInteger:
        display_plates = paginator.page(1)
    except EmptyPage:
        display_plates = paginator.page(paginator.num_pages)

    context = {
        'library_plates': library_plates,
        'paginated': display_plates,
    }

    return render(request, 'library_plates.html', context)


def library_plate(request, id):
    """Render the page showing the contents of a single library plate."""
    library_plate = get_object_or_404(LibraryPlate, pk=id)
    library_wells = LibraryWell.objects.filter(
        plate=library_plate).order_by('well')
    for library_well in library_wells:
        library_well.row = library_well.get_row()

    context = {
        'library_plate': library_plate,
        'library_wells': library_wells,
    }

    return render(request, 'library_plate.html', context)
