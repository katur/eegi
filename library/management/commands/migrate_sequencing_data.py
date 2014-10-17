import csv
import glob
import sys

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from library.models import LibrarySequencing

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
                                               row['tracking_number'].strip())


def update_LibrarySequencing_table(genewiz_output_root, tracking_number):
    qscrl_filepath = ('{}/{}_QSCRL.txt'.format(genewiz_output_root,
                                               tracking_number))
    try:
        qscrl_file = open(qscrl_filepath, 'rb')

    except IOError as e:
        sys.stderr.write('QSCRL file missing or could not be open '
                         'for tracking number {}. I/O error({}): {}\n'
                         .format(tracking_number, e.errno, e.strerror))
        return

    with qscrl_file:
        qscrl_reader = csv.DictReader(qscrl_file, delimiter='\t')
        for row in qscrl_reader:
            # Need tracking number and tube label because they are the fields
            # that genewiz uses to uniquely define sequences, in the case of
            # resequencing.
            tracking_number = row['trackingNumber']
            tube_label = row['TubeLabel']
            dna_name = row['DNAName']

            # Need sample plate namd and sample tube number because they are
            # what we name our samples (to identify what sequence well came
            # from what library well).
            # Note that tube_label can't be used for sample_tube_number
            # because it is often 1-2 instead of 95-96
            sample_plate_name = get_plate_name_from_dna_name(dna_name)
            sample_tube_number = get_tube_number_from_dna_name(dna_name)

            timestamp = row['Created_Dttm']

            # avoid Template_Name... sometimes e.g. 'GC1'

            if '_R' in tube_label:
                dna_name += '_R'

            seq_filepath = ('{}/{}_seq/{}_*.seq'.format(genewiz_output_root,
                                                        tracking_number,
                                                        dna_name))
            try:
                seq_file = open(glob.glob(seq_filepath)[0], 'rb')

            except IOError:
                sys.stderr.write('Seq file missing for tracking number '
                                 '{}, dna {}\n'
                                 .format(tracking_number, dna_name))
            with seq_file:
                ab1_filename = seq_file.next()
                ab1_filename = ab1_filename.strip()
                ab1_filename = ab1_filename.split('>')[1]

                sequence = ''
                for seq_row in seq_file:
                    sequence += seq_row.strip()

            try:
                LibrarySequencing.objects.get(
                    genewiz_tracking_number=tracking_number,
                    genewiz_tube_label=tube_label)
            except ObjectDoesNotExist:
                new_sequence = LibrarySequencing(
                    sample_plate_name=sample_plate_name,
                    sample_tube_number=sample_tube_number,
                    genewiz_tracking_number=tracking_number,
                    genewiz_tube_label=tube_label,
                    sequence=sequence,
                    ab1_filename=ab1_filename,
                    quality_score=row['QualityScore'],
                    crl=row['CRL'],
                    qv20plus=row['QV20Plus'],
                    si_a=row['SI_A'],
                    si_c=row['SI_C'],
                    si_g=row['SI_G'],
                    si_t=row['SI_T']
                )
                new_sequence.save()


def get_plate_name_from_dna_name(dna_name):
    return dna_name.split('_')[0]


def get_tube_number_from_dna_name(dna_name):
    try:
        return int(dna_name.split('_')[1].split('-')[0])
    except ValueError:
        raise ValueError('dna_name {} parsed with a non-int tube number'
                         .format(dna_name))
