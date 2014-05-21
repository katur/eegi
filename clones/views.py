from django.shortcuts import render
from clones.models import ClonePlate


def clone_plates(request):
    clone_plates = sorted(ClonePlate.objects.all())
    context = {'clone_plates': clone_plates}
    return render(request, 'clone_plates.html', context)
