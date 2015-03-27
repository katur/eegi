import sys

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from clones.models import Clone

HELP = '''
Compare the Ahringer library as listed in the database (which was derived from
Huey-Ling's version in GenomeWideGI), to that currently listed online
at Source BioScience.

The input file should be copied from this Source BioScience webpage:

http://www.lifesciences.sourcebioscience.com/clone-products/non-mammalian/
    c-elegans/c-elegans-rnai-library/celegans-database/

'''


class Command(BaseCommand):
    args = 'input_file'
    help = HELP

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError()

        ahringer_db = set()
        ahringer_online = set()

        for clone in Clone.objects.filter(id__startswith='sjj'):
            ahringer_db.add(clone)

        with open(args[0], 'rb') as f:
            # Skip header
            f.readline()

            for line in f:
                row = line.split()
                clone_name = 'sjj_' + row[3]
                try:
                    clone = Clone.objects.get(pk=clone_name)
                    ahringer_online.add(clone)

                except ObjectDoesNotExist:
                    sys.exit('{} not in db\n'.format(clone_name))

        ahringer_online_only = ahringer_online.difference(ahringer_db)
        ahringer_db_only = ahringer_db.difference(ahringer_online)

        sys.stdout.write('{} sjj clones listed online\n'
                         '{} sjj clones in database\n'
                         '{} sjj clones online ONLY\n'
                         '{} sjj clones in database ONLY\n'
                         .format(len(ahringer_online),
                                 len(ahringer_db),
                                 len(ahringer_online_only),
                                 len(ahringer_db_only)))
