import csv
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from clones.models import Clone
from library.models import LibraryWell, LibrarySequencing


class Command(BaseCommand):
    """
    Command to migrate the sequencing data.

    USAGE
    From the project root:
        ./manage.py migrate_blat_data blat_csv
    """
    help = ('Migrate blat data from csv to the database.')

    def handle(self, *args, **options):
        if len(args) != 1:
            sys.exit(
                'Usage:\n'
                '\t./manage.py migrate_blat_data blat_csv\n'
            )

        proceed = False
        while not proceed:
            sys.stdout.write('This script modifies the database. '
                             'Proceed? (yes/no): ')
            response = raw_input()
            if response == 'no':
                sys.stdout.write('Okay. Goodbye!\n')
                sys.exit(0)
            elif response != 'yes':
                sys.stdout.write('Please try again, '
                                 'responding "yes" or "no"\n')
                continue
            else:
                proceed = True

        with open(args[0], 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            absent = set()

            for row in reader:
                query_pk = row['query_pk']
                clone_hit = row['clone_hit']
                e_value = row['e_value']
                bit_score = row['bit_score']
                hit_rank = row['hit_rank']

                try:
                    sequencing = LibrarySequencing.objects.get(pk=query_pk)
                except ObjectDoesNotExist:
                    sys.exit('query_pk {} not found in LibrarySequencing'
                             .format(query_pk))

                try:
                    clone = Clone.objects.get(pk=clone_hit)
                except ObjectDoesNotExist:
                    absent.add(clone_hit)
                    continue

                try:
                    e_value = float(e_value)
                except ValueError:
                    sys.exit('e_value {} not convertible to float'
                             .format(e_value))

                try:
                    bit_score = int(float(bit_score))
                except ValueError:
                    sys.exit('bit_score {} not convertible to int'
                             .format(bit_score))

                try:
                    hit_rank = int(hit_rank)
                except ValueError:
                    sys.exit('hit_rank {} not convertible to int'
                             .format(hit_rank))

            sys.stdout.write('{} sjj clones not present in database\n'
                             .format(len(absent)))
