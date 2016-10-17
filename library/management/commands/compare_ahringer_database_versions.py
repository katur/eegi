import argparse

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from clones.models import Clone


class Command(BaseCommand):
    """
    Command to compare the Ahringer library as in the database to another.

    Currently, this is useful for comparing the library as listed in the
    database (currently derived from Huey-Ling's version in GenomeWideGI)
    to that currently listed online at Source BioScience:

        http://www.lifesciences.sourcebioscience.com/clone-products/non-mammalian/
            c-elegans/c-elegans-rnai-library/celegans-database/

    The input file can be copied/pasted from the above link.
    """

    help = "Compare this database's Ahringer library to another version"

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'),
                            help="Ahringer library from Source BioScience. "
                                 "See this command's docstring "
                                 "for more details.")

    def handle(self, **options):
        f = options['file']

        # Get Ahringer clones in this database
        ahringer_db = set()
        for clone in Clone.objects.filter(id__startswith='sjj'):
            ahringer_db.add(clone)

        # Get Ahringer clones from Source BioScience
        ahringer_online = set()

        # Skip header
        f.readline()

        for line in f:
            row = line.split(',')
            clone_name = 'sjj_' + row[3]
            try:
                clone = Clone.objects.get(pk=clone_name)
                ahringer_online.add(clone)

            except ObjectDoesNotExist:
                raise CommandError('{} not in db\n'.format(clone_name))

        ahringer_online_only = ahringer_online.difference(ahringer_db)
        ahringer_db_only = ahringer_db.difference(ahringer_online)

        self.stdout.write('{} sjj clones in this database\n'
                          '{} sjj clones in input file\n'
                          '{} sjj clones in this database ONLY\n'
                          '{} sjj clones in input file ONLY\n'
                          .format(len(ahringer_db),
                                  len(ahringer_online),
                                  len(ahringer_db_only),
                                  len(ahringer_online_only)))
