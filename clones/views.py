from django.shortcuts import render
from clones.models import Clone


def clones(request):
    clones = Clone.objects.all()
    context = {'clones': clones}
    return render(request, 'clones.html', context)
