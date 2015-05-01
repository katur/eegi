import argparse

from django.core.management.base import BaseCommand


HELP = '''
Format the Enhancer Secondary screen cherry-picking list such that it
is easier to cherry-pick from.

'''


class Command(BaseCommand):
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'))

    def handle(self, **options):
        f = options['file']

        # print header
        self.stdout.write(f.readline())

        # Keep track of source/destination plate combos in order
        # to partition results by this (helps techs to cherry pick)
        num_combos = 0
        previous_combo = (None, None)

        destination_plates = set()
        empties = []

        for line in f:
            row = line.split(',')
            source_plate = row[0]
            destination_plate = row[2]

            if source_plate is None:
                empties.append(row)

            destination_plates.add(destination_plate)

            current_combo = (source_plate, destination_plate)
            if current_combo != previous_combo:
                num_combos += 1
                previous_combo = current_combo
                self.stdout.write('\n')

            self.stdout.write(','.join([str(x) for x in row]))

        self.stdout.write('\n\n{} destination plates.'
                          '\n\n{} origin/destination combos.'
                          .format(len(destination_plates),
                                  num_combos))
