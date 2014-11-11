import csv
# import datetime
import glob
import MySQLdb
import sys
import xlrd

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from library.models import LibraryWell, LibrarySequencing

from eegi.local_settings import LEGACY_DATABASE


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

    USAGE
    From the project root:
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

        # First add all raw genewiz output, including actual sequence and
        # various quality scores, for GI sequences only (distinguished
        # from sequencing for other lab members by being in the
        # tracking_numbers file)
        with open(tracking_numbers, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                process_genewiz_tracking_number(genewiz_output_root,
                                                row['tracking_number'].strip())

        # Retrieve all the sequencing objects just recorded
        all_recorded_sequences = LibrarySequencing.objects.all()

        # Connect to legacy database for updating the source of sequencing
        # plates 1-56.
        legacy_db = MySQLdb.connect(host=LEGACY_DATABASE['HOST'],
                                    user=LEGACY_DATABASE['USER'],
                                    passwd=LEGACY_DATABASE['PASSWORD'],
                                    db=LEGACY_DATABASE['NAME'])
        cursor = legacy_db.cursor()

        # Create a dictionary to translate from sequencing well to tube number,
        # because all 96 tubes are not recorded in the legacy database
        # (legacy database skips empty wells).
        # Choose SeqPlateID=1 because it happens to have all 96 wells.
        cursor.execute('SELECT tubeNum, Seq96well FROM SeqPlate '
                       'WHERE SeqPlateID=1')
        seq_well_to_tube = {}
        for row in cursor.fetchall():
            seq_well_to_tube[row[1]] = row[0]

        # Query legacy database for recorded sequence sources (plates 1-56).
        legacy_query = ('SELECT RNAiPlateID, 96well, SeqPlateID, Seq96Well, '
                        'oriClone, receiptID FROM SeqPlate')
        cursor.execute(legacy_query)
        legacy_rows = cursor.fetchall()

        for row in legacy_rows:
            process_legacy_row(row, all_recorded_sequences, seq_well_to_tube)

        full_plates = {
            57: 'hybrid_F1',
            58: 'hybrid_F2',
            59: 'hybrid_F3',
            60: 'hybrid_F4',
            61: 'hybrid_F5',
            62: 'hybrid_F6',
            63: 'universal_F5',
            64: 'or346_F6',
            65: 'or346_F7',
            66: 'mr17_F3',
        }


def process_legacy_row(row, all_recorded_sequences, seq_well_to_tube):
    # The plate and well that the sequencing result came from
    source_plate_id = row[0]
    source_well = row[1]

    # Identifying information for the plate/tube that were sequenced
    sample_plate_name = 'JL' + str(row[2])
    sample_well = row[3]
    sample_tube_number = seq_well_to_tube[sample_well]

    # Legacy clone and legacy tracking just for double checking
    if len(row) > 4:
        legacy_clone = row[4]
        legacy_tracking = row[5]

    recorded_sequences = all_recorded_sequences.filter(
        sample_plate_name=sample_plate_name,
        sample_tube_number=sample_tube_number)

    if not recorded_sequences:
        sys.stderr.write('No record in new database for sequencing '
                         'record {} {}\n'.format(sample_plate_name,
                                                 sample_tube_number))
    else:
        for sequence in recorded_sequences:
            if (legacy_tracking and
                    legacy_tracking != sequence.genewiz_tracking_number):
                sys.stderr.write('Tracking number mismatch for '
                                 'sequencing record {} {}\n'.format(
                                     sample_plate_name,
                                     sample_tube_number))
            source_library_well_id = '{}_{}'.format(source_plate_id,
                                                    source_well)
            try:
                source_library_well = LibraryWell.objects.get(
                    pk=source_library_well_id)
                try:
                    # Double check that clone matches
                    clone = source_library_well.intended_clone.id
                    if (legacy_clone and ('GHR' not in clone)
                            and clone != legacy_clone):
                        sys.stderr.write(
                            'Clone mismatch for {} {}: {} {}\n'
                            .format(source_plate_id, source_well,
                                    clone, legacy_clone))

                except AttributeError:
                    # Due to a few wells with no intended clone
                    # being sequenced
                    sys.stderr.write('LibraryWell {} has no intended clone\n'
                                     .format(source_library_well_id))

                # Save the source well, regardless of clone issues
                sequence.source_library_well = source_library_well
                sequence.save()

            except ObjectDoesNotExist:
                # Due to Hueyling deleting from CherryPickRNAiPlate
                # the wells that did not grow, but not deleting these
                # from CherryPickTemplate or SeqPlate.
                # When I go back and add all empty wells to be
                # represented, these should get added.
                sys.stderr.write('LibraryWell {} not found\n'
                                 .format(source_library_well_id))


def process_genewiz_tracking_number(genewiz_output_root, tracking_number):
    qscrl_txt = ('{}/{}_QSCRL.txt'.format(genewiz_output_root,
                                          tracking_number))
    qscrl_xls = ('{}/{}_QSCRL.xls'.format(genewiz_output_root,
                                          tracking_number))
    try:
        qscrl_file = open(qscrl_txt, 'rb')
        with qscrl_file:
            qscrl_reader = csv.DictReader(qscrl_file, delimiter='\t')
            for row in qscrl_reader:
                # Need tracking number and tube label because they are the
                # fields that genewiz uses to uniquely define sequences,
                # in the case of resequencing.
                process_qscrl_row(row, genewiz_output_root, tracking_number)

    except IOError:
        try:
            book = xlrd.open_workbook(qscrl_xls, on_demand=True)
            sheet = book.sheet_by_name(tracking_number)
            keys = [sheet.cell(4, col_index).value
                    for col_index in xrange(sheet.ncols)]
            for row_index in xrange(5, sheet.nrows):
                row = {}
                for col_index in xrange(sheet.ncols):
                    # cell_type = sheet.cell_type(row_index, col_index)
                    cell_value = sheet.cell_value(row_index, col_index)

                    '''
                    if cell_type == xlrd.XL_CELL_DATE:
                        dt_tuple = xlrd.xldate_as_tuple(cell_value,
                                                        book.datemode)
                        cell_value = datetime.datetime(
                            dt_tuple[0], dt_tuple[1], dt_tuple[2],
                            dt_tuple[3], dt_tuple[4], dt_tuple[5]
                        )
                    '''
                    row[keys[col_index]] = cell_value

                process_qscrl_row(row, genewiz_output_root, tracking_number)
            '''
            num_rows = worksheet.nrows - 1
            curr_row = 3
            while curr_row < num_rows:
                curr_row += 1
                row = worksheet.row(curr_row)
                print row
            '''

        except IOError as e:
            sys.stderr.write('QSCRL file missing or could not be open '
                             'for tracking number {}. I/O error({}): {}\n'
                             .format(tracking_number, e.errno, e.strerror))
            return


def process_qscrl_row(row, genewiz_output_root, tracking_number):
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

    # timestamp = row['Created_Dttm']

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
