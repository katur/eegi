from library.models import LibraryStock


def get_organized_library_stocks(screen_stage=None):
    """Fetch all library stocks from the database, organized as:

        l[plate][well] = library_stock

    Optionally provide integer screen_stage, to limit to that screen.

    """
    stocks = LibraryStock.objects.select_related('plate')

    if screen_stage:
        stocks = stocks.filter(plate__screen_stage=screen_stage)
    else:
        stocks = stocks.all()

    return _organize_library_stocks(stocks)


def _organize_library_stocks(library_stocks):
    """Organize library_stocks into the format:

        l[plate][well] = library_stock

    """
    l = {}
    for library_stock in library_stocks:
        plate = library_stock.plate
        well = library_stock.well
        if plate not in l:
            l[plate] = {}
        l[plate][well] = library_stock

    return l
