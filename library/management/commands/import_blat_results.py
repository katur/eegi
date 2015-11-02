import argparse
import csv

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from clones.models import Clone
from library.models import LibrarySequencing, LibrarySequencingBlatResult
from utils.scripting import require_db_write_acknowledgement

HELP = '''
Import the BLAT hits of our sequencing results to the database.

This script starts by clearing the LibrarySequencingBlatResult table.
It is okay to do this because no other tables depend on
LibrarySequencingBlatResult.

The input_file is the csv provided by Firoz. It is currently at:

    materials/sequencing/blat_results_from_firoz/BLAT_RES_eegi_seq3_all_ranking.txt

'''


class Command(BaseCommand):
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'))

    def handle(self, **options):
        f = options['file']

        require_db_write_acknowledgement()

        LibrarySequencingBlatResult.objects.all().delete()

        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            query_pk = row['query_pk']
            clone_hit = row['clone']
            e_value = row['BLAT_e-value']
            bit_score = row['bit_score']
            hit_rank = row['hit_rank']

            try:
                sequencing = LibrarySequencing.objects.get(pk=query_pk)
            except ObjectDoesNotExist:
                raise CommandError('query_pk {} not found in '
                                   'LibrarySequencing'
                                   .format(query_pk))

            try:
                clone = Clone.objects.get(pk=clone_hit)
            except ObjectDoesNotExist:
                raise CommandError('clone_hit {} not present in database'
                                   .format(clone_hit))

            try:
                e_value = float(e_value)
            except ValueError:
                raise CommandError('e_value {} not convertible to float'
                                   .format(e_value))

            try:
                bit_score = int(float(bit_score))
            except ValueError:
                raise CommandError('bit_score {} not convertible to int'
                                   .format(bit_score))

            try:
                hit_rank = int(hit_rank)
            except ValueError:
                raise CommandError('hit_rank {} not convertible to int'
                                   .format(hit_rank))

            result = LibrarySequencingBlatResult(
                library_sequencing=sequencing,
                clone_hit=clone,
                e_value=e_value,
                bit_score=bit_score,
                hit_rank=hit_rank
            )

            result.save()
