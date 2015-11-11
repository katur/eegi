import argparse
import csv

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from clones.models import Clone
from library.models import LibrarySequencing, LibrarySequencingBlatResult
from utils.scripting import require_db_write_acknowledgement

HELP = 'Import the BLAT hits of our sequencing results.'


class Command(BaseCommand):
    """Command to import Firoz's BLAT hits of our sequencing results.

    This script starts by clearing the LibrarySequencingBlatResult table.
    It is okay to do this because no other tables depend on
    LibrarySequencingBlatResult.

    The input is the CSV file provided by Firoz, with a few simple UNIX
    transformations. The transformed file currently lives at:

        materials/sequencing/blat_results_from_firoz/joined

    The transformation script, which explains itself:

        materials/sequencing/blat_results_from_firoz/transform

    """
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'),
                            help="CSV of BLAT hits from Firoz. "
                                 "See this command's docstring "
                                 "for more details.")

    def handle(self, **options):
        f = options['file']

        require_db_write_acknowledgement()

        LibrarySequencingBlatResult.objects.all().delete()

        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            genewiz_tracking_number = row['genewiz_tracking_number']
            genewiz_tube_label = row['genewiz_tube_label']
            clone_hit = row['clone']
            e_value = row['BLAT_e-value']
            bit_score = row['bit_score']
            hit_rank = row['hit_rank']

            try:
                sequencing = LibrarySequencing.objects.get(
                    genewiz_tracking_number=genewiz_tracking_number,
                    genewiz_tube_label=genewiz_tube_label)
            except ObjectDoesNotExist:
                raise CommandError('Genewiz tracking {}, tube {} not found in '
                                   'LibrarySequencing'
                                   .format(genewiz_tracking_number,
                                           genewiz_tube_label))

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
