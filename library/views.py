from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from library.models import LibraryPlate, LibraryWell


def library_plates(request):
    screen_stage = request.GET.get('screen_stage')
    if screen_stage:
        plates = sorted(LibraryPlate.objects.filter(
            screen_stage=screen_stage))
    else:
        plates = sorted(LibraryPlate.objects.filter(
            screen_stage__gte=1))

    paginator = Paginator(plates, 50)
    page = request.GET.get('page')

    try:
        display_plates = paginator.page(page)
    except PageNotAnInteger:
        display_plates = paginator.page(1)
    except EmptyPage:
        display_plates = paginator.page(paginator.num_pages)

    context = {
        'plates': plates,
        'display_plates': display_plates,
    }

    return render(request, 'library_plates.html', context)


def library_plate(request, id):
    plate = get_object_or_404(LibraryPlate, pk=id)
    wells = LibraryWell.objects.filter(plate=plate).order_by('well')
    for well in wells:
        well.row = well.get_row()

    context = {
        'plate': plate,
        'wells': wells,
    }

    return render(request, 'library_plate.html', context)
