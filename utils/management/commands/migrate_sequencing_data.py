import sys
import csv

from django.core.management.base import BaseCommand, CommandError

# from eegi.local_settings import LEGACY_DATABASE


class Command(BaseCommand):
    """
    Command to migrate the sequencing data.

    REQUIREMENTS
    Requires connection info for legacy database in local_settings, in format:
    LEGACY_DATABASE = {
        'NAME': 'GenomeWideGI',
        'HOST': 'localhost',
        'USER': 'my_username',
        'PASSWORD': 'my_password',
    }

    Some steps require that the WormStrain table is already populated.


    USAGE
    To update all tables, execute as so (from the project root):
    ./manage.py migrate_sequencing_data tracking_numbers genewiz_output_root
    """
    help = ('Update the sequencing information in the new database.')

    def handle(self, *args, **options):
        if len(args) != 2:
            sys.exit(
                'Usage:\n'
                '\t./manage.py migrate_sequencing_data '
                'tracking_numbers genewiz_output_root\n'
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

        tracking_numbers = args[0]
        genewiz_output_root = args[1]

        '''
        legacy_db = MySQLdb.connect(host=LEGACY_DATABASE['HOST'],
                                    user=LEGACY_DATABASE['USER'],
                                    passwd=LEGACY_DATABASE['PASSWORD'],
                                    db=LEGACY_DATABASE['NAME'])
        cursor = legacy_db.cursor()
        '''

        with open(tracking_numbers, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                update_LibrarySequencing_table(genewiz_output_root,
                                               row['tracking_number'])
                break


def update_LibrarySequencing_table(genewiz_output_root, tracking_number):
    try:
        filename = ('{}/{}_QSCRL.txt'
                    .format(genewiz_output_root, tracking_number))
        with open(filename, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            for row in reader:
                # Identification
                tracking_number = row['trackingNumber']
                tube_label = row['TubeLabel']
                dna_name = row['DNAName']
                template_name = row['Template_Name']
                time_created = row['Created_Dttm']

                # Quality
                quality_score = row['QualityScore']
                crl = row['CRL']
                qv20plus= row['QV20Plus']
                si_a = row['SI_A']
                si_c = row['SI_C']
                si_g = row['SI_G']
                si_t = row['SI_T']
        print '\n\n\n\n\n\n'

    except IOError:
        print 'file does not exit'
