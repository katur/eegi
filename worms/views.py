from django.shortcuts import render
from worms.models import WormStrain


def worm_strains(request):
    worm_strains = WormStrain.objects.all()
    for strain in worm_strains:
        strain.url = strain.get_lab_website_url()
        strain.permissive_temperature = strain.get_permissive_string()
        strain.restrictive_temperature = strain.get_restrictive_string()

    context = {'strains': worm_strains}
    return render(request, 'worm_strains.html', context)
