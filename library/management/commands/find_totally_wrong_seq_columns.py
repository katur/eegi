from django.core.management.base import BaseCommand

from clones.helpers.queries import get_l4440
from library.models import LibraryStock


class Command(BaseCommand):

    help = ('From SUP secondary plates, find columns with zero '
            'cases where the intended clones matches a BLAT hit.')

    def handle(self, **options):
        l4440 = get_l4440()

        # Get all non-L4440, non-null, SUP secondary LibraryStocks
        stocks = (LibraryStock.objects
                  .exclude(intended_clone=l4440)
                  .exclude(intended_clone__isnull=True)
                  .filter(plate__screen_stage=2, plate__id__contains='F'))

        d = group_by_plate_then_column(stocks)

        for plate, columns in d.iteritems():
            for column, stocks in columns.iteritems():
                has_a_matching_stock = False

                for stock in stocks:
                    if stock.has_sequencing_match():
                        has_a_matching_stock = True

                if not has_a_matching_stock:
                    self.stdout.write('Column {} of plate {} has no match'
                                      .format(column, plate))

                    for stock in stocks:
                        self.stdout.write(_get_stock_string(stock))


def _get_stock_string(stock):
    return ('\tStock {}, intended clone {}, top hits {}'
            .format(stock, stock.intended_clone,
                    stock.get_sequencing_hits(top_hit_only=True)))


def group_by_plate_then_column(stocks):
    # d[plate][column] = [stocks]
    d = {}

    for stock in stocks:
        plate = stock.plate
        column = stock.get_column()

        if plate not in d:
            d[plate] = {}

        if column not in d[plate]:
            d[plate][column] = []

        d[plate][column].append(stock)

    return d
