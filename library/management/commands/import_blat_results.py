import argparse
import csv

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from clones.models import Clone
from library.models import LibrarySequencing, LibrarySequencingBlatResult
from utils.scripting import require_db_write_acknowledgement


class Command(BaseCommand):
    """
    Command to import Firoz's BLAT hits of our sequencing results.

    The input is a CSV with column names:

        sequencing_id
        clone_hit
        e_value
        bit_score
        hit_rank

    This script expects tab-delimited, since that is what Firoz gave us
    last time. Just change the delimiter in the code below if this changes.

    Since we last imported BLAT results this way, the primary key of
    LibrarySequencing has changed from INT to VARCHAR (now made up of
    the genewiz tracking number and tube label). This should hardly
    affect his script, except that he may need to change the type of
    this variable from int to string, and he might need to update the
    CSV column names of his output to match the spec above.
    """

    help = 'Import the BLAT hits of our sequencing results.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'),
                            help="CSV of BLAT hits from Firoz. "
                                 "See this command's docstring "
                                 "for more details.")

    def handle(self, **options):
        require_db_write_acknowledgement()

        f = options['file']

        reader = csv.DictReader(f, delimiter='\t')

        for row in reader:
            sequencing_id = row['sequencing_id']
            clone_hit = row['clone_hit']
            e_value = row['e_value']
            bit_score = row['bit_score']
            hit_rank = row['hit_rank']

            try:
                sequencing = LibrarySequencing.objects.get(id=sequencing_id)
            except ObjectDoesNotExist:
                raise CommandError('ID {} not found in LibrarySequencing'
                                   .format(sequencing_id))

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
                sequencing=sequencing,
                clone_hit=clone,
                e_value=e_value,
                bit_score=bit_score,
                hit_rank=hit_rank
            )

            result.save()
