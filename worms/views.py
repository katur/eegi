from django.shortcuts import render
from worms.models import WormStrain


def worms(request):
    """
    Render the page that shows all worm strains used in the screen.
    """
    worms = WormStrain.objects.all()
    for worm in worms:
        worm.url = worm.get_url(request)

    context = {'worms': worms}
    return render(request, 'worms.html', context)
