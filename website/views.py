from django.shortcuts import render

from eegi.settings import (BATCH_DATA_ENTRY_GDOC_NAME,
                           BATCH_DATA_ENTRY_GDOC_URL)


def home(request):
    """Render the homepage."""
    return render(request, 'home.html')


def help_page(request):
    """Render the help page."""
    context = {
        'batch_data_entry_gdoc_url': BATCH_DATA_ENTRY_GDOC_URL,
        'batch_data_entry_gdoc_name': BATCH_DATA_ENTRY_GDOC_NAME,
    }

    return render(request, 'help.html', context)
