import argparse

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to format a cherry-pick list so that it is easier for techs
    to cherry-pick from.

    Simply adds blank lines at the points where the techs would need to
    change the plates in front of them.

    Arguments

    - file should be a comma-separated file, including header row,
      where each row is in format:

        source_plate,source_well,destination_plate,destination_well

    """
    help = 'Format a cherry-pick list for techs.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'),
                            help="CSV of cherry-pick list. "
                                 "See this command's docstring "
                                 "for more details.")

    def handle(self, **options):
        f = options['file']

        # Print header
        self.stdout.write(f.readline())

        # Keep track of source/destination plate combos in order
        # to partition results by this (helps techs to cherry pick)
        num_combos = 0
        previous_combo = (None, None)

        destination_plates = set()

        for line in f:
            row = line.split(',')
            source_plate = row[0]
            destination_plate = row[2]

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
