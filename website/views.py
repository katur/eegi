from django.conf import settings
from django.shortcuts import render


def home(request):
    """Render the homepage."""
    return render(request, 'home.html')


def help_page(request):
    """Render the help page."""
    context = {
        'batch_data_entry_gdoc_url': settings.BATCH_DATA_ENTRY_GDOC_URL,
        'batch_data_entry_gdoc_name': settings.BATCH_DATA_ENTRY_GDOC_NAME,
    }

    return render(request, 'help.html', context)
