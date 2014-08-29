from django.shortcuts import render
from worms.models import WormStrain


def worm_strains(request):
    worm_strains = WormStrain.objects.all()
    context = {'strains': worm_strains}
    return render(request, 'worm_strains.html', context)
