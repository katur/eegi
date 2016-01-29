from django.shortcuts import render


def home(request):
    """Render the homepage."""
    return render(request, 'home.html')


def help_page(request):
    """Render the help page."""
    return render(request, 'help.html')
