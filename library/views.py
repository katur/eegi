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
        plates_to_display = paginator.page(page)
    except PageNotAnInteger:
        plates_to_display = paginator.page(1)
    except EmptyPage:
        plates_to_display = paginator.page(paginator.num_pages)

    context = {
        'plates': plates,
        'plates_to_display': plates_to_display,
    }
    return render(request, 'library_plates.html', context)
