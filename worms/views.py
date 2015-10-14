from django.shortcuts import render

from worms.models import WormStrain


def worms(request):
    """Render the page listing all worm strains used in the screen."""
    worms = WormStrain.objects.all()
    context = {'worms': worms}
    return render(request, 'worms.html', context)
