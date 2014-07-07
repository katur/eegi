from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from clones.models import ClonePlate


def clone_plates(request):
    clone_plates = sorted(ClonePlate.objects.all())
    paginator = Paginator(clone_plates, 25)

    page = request.GET.get('page')
    try:
        clone_plates = paginator.page(page)
    except PageNotAnInteger:
        clone_plates = paginator.page(1)
    except EmptyPage:
        clone_plates = paginator.page(paginator.num_pages)

    context = {'clone_plates': clone_plates}
    return render(request, 'clone_plates.html', context)
