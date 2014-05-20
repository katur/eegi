from django.shortcuts import render
from wormstrains.models import WormStrain


def strains(request):
    strains = WormStrain.objects.all()
    for strain in strains:
        strain.url = strain.get_wormbase_url()
    context = {'strains': strains}
    return render(request, 'strains.html', context)
