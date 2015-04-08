import os.path

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from clones.models import Clone

HELP = '''
Get some quick stats comparing the Ahringer library as listed in the database
to another version.

Currently, this is useful for comparing the library as listed in the database
(currently derived from Huey-Ling's version in GenomeWideGI)
to that currently listed online at Source BioScience:

    http://www.lifesciences.sourcebioscience.com/clone-products/non-mammalian/
        c-elegans/c-elegans-rnai-library/celegans-database/

The input_file is currently at:

    materials/ahringer_plates/sourcebioscience_c_elegans_database

'''


class Command(BaseCommand):
    args = 'input_file'
    help = HELP

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Command requires 1 argument')

        filename = args[0]
        if not os.path.isfile(filename):
            raise CommandError('File not found')

        ahringer_db = set()
        ahringer_online = set()

        for clone in Clone.objects.filter(id__startswith='sjj'):
            ahringer_db.add(clone)

        with open(filename, 'rb') as f:
            # Skip header
            f.readline()

            for line in f:
                row = line.split()
                clone_name = 'sjj_' + row[3]
                try:
                    clone = Clone.objects.get(pk=clone_name)
                    ahringer_online.add(clone)

                except ObjectDoesNotExist:
                    raise CommandError('{} not in db\n'.format(clone_name))

        ahringer_online_only = ahringer_online.difference(ahringer_db)
        ahringer_db_only = ahringer_db.difference(ahringer_online)

        self.stdout.write('{} sjj clones in database\n'
                          '{} sjj clones in input_file\n'
                          '{} sjj clones in database ONLY\n'
                          '{} sjj clones in input_file ONLY\n'
                          .format(len(ahringer_db),
                                  len(ahringer_online),
                                  len(ahringer_db_only),
                                  len(ahringer_online_only)))
