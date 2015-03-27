import csv
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from clones.models import Clone
from library.models import LibrarySequencing, LibrarySequencingBlatResult
from utils.helpers.scripting import require_db_write_acknowledgement

HELP = '''
Migrate the BLAT hits of our sequencing results to the database.

The input file is the csv provided by Firoz.
'''


class Command(BaseCommand):
    args = 'input_file'
    help = HELP

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError()

        require_db_write_acknowledgement()

        LibrarySequencingBlatResult.objects.all().delete()

        with open(args[0], 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            absent = set()

            for row in reader:
                query_pk = row['query_pk']
                clone_hit = row['clone']
                e_value = row['BLAT_e-value']
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

                result = LibrarySequencingBlatResult(
                    library_sequencing=sequencing,
                    clone_hit=clone,
                    e_value=e_value,
                    bit_score=bit_score,
                    hit_rank=hit_rank
                )
                result.save()

            sys.stdout.write('{} clones not present in database\n'
                             .format(len(absent)))
