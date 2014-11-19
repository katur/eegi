from django.shortcuts import render
from worms.models import WormStrain


def worm_strains(request):
    """
    Render the page that shows all worm strains used in the screen.
    """
    worm_strains = WormStrain.objects.all()
    for strain in worm_strains:
        strain.url = strain.get_url(request)

    context = {'strains': worm_strains}
    return render(request, 'worm_strains.html', context)
