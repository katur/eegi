from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from library.models import LibraryPlate


def library_plates(request):
    screen_stage = request.GET.get('screen_stage')
    if screen_stage:
        plates = sorted(LibraryPlate.objects.filter(
            screen_stage=screen_stage))
    else:
        plates = sorted(LibraryPlate.objects.all())

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
