import csv
# import datetime
import glob
import MySQLdb
import sys
import xlrd

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from eegi.local_settings import LEGACY_DATABASE
from library.models import LibraryWell, LibrarySequencing
from utils.helpers.well_tile_conversion import get_well_name
from utils.helpers.scripting import require_db_write_acknowledgement


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
    ./manage.py migrate_genewiz_data tracking_numbers_csv genewiz_data_root
    """
    help = ('Update the sequencing information in the new database.')

    def handle(self, *args, **options):
        if len(args) != 2:
            sys.exit(
                'Usage:\n'
                '\t./manage.py migrate_genewiz_data '
                'tracking_numbers_csv genewiz_data_root\n'
            )

        require_db_write_acknowledgement()

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

        full_seq_plates = {
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

        for seq_plate_number in full_seq_plates:
            source_plate_id = full_seq_plates[seq_plate_number]
            library_wells = LibraryWell.objects.filter(plate=source_plate_id)
            for library_well in library_wells:
                row = (source_plate_id, library_well.well, seq_plate_number,
                       library_well.well)
                process_legacy_row(row, all_recorded_sequences,
                                   seq_well_to_tube)

        full_seq_columns = {
            67: {
                1: ('hc69_F7', 1),
                2: ('hc69_F7', 3),
                3: ('hc69_F7', 4),
                4: ('hc69_F7', 5),
                5: ('g53_F2', 8),
                6: ('g53_F2', 9),
                7: ('g53_F2', 10),
                8: ('it5_F3', 4, 'DEFGH'),
                9: ('it5_F3', 5),
                10: ('it57_F4', 4, 'GH'),
                11: ('ye60_F2', 8),
                12: ('b244_F1', 12),
            },
            68: {
                1: ('or191_F1', 1),
                2: ('or191_F1', 3),
                3: ('or191_F1', 4),
                4: ('or191_F1', 5),
                5: ('or191_F1', 6),
                6: ('or191_F1', 8),
                7: ('or191_F1', 9),
                8: ('or191_F1', 10),
                9: ('or191_F1', 12),
                10: ('or191_F2', 1),
                11: ('or191_F2', 3),
                12: ('or191_F2', 4),
            },
            69: {
                1: ('or191_F2', 5),
                2: ('or191_F2', 6),
                3: ('or191_F2', 8),
                4: ('or191_F2', 9),
                5: ('or191_F2', 10),
                6: ('or191_F2', 12),
                7: ('or191_F3', 1),
                8: ('or191_F3', 3),
                9: ('b235_F5', 1),
                10: ('b235_F5', 3),
                11: ('b235_F5', 4),
                12: ('b235_F5', 5),
            },
            70: {
                1: ('b235_F5', 6),
                2: ('b235_F5', 8),
                3: ('b235_F5', 9),
                4: ('b235_F5', 10),
                5: ('b235_F5', 12),
                6: ('b235_F6', 1),
                7: ('b235_F6', 3),
                8: ('b235_F6', 4),
                9: ('b235_F6', 5),
                10: ('b235_F6', 6),
                11: ('b235_F6', 8),
                12: ('b235_F6', 9),
            },
        }

        for seq_plate_number in full_seq_columns:
            seq_columns = full_seq_columns[seq_plate_number]
            for seq_column in seq_columns:
                source_plate_id = seq_columns[seq_column][0]
                source_column = seq_columns[seq_column][1]
                if len(seq_columns[seq_column]) > 2:
                    letters = seq_columns[seq_column][2]
                else:
                    letters = 'ABCDEFGH'
                for letter in letters:
                    seq_well = get_well_name(letter, seq_column)
                    source_well = get_well_name(letter, source_column)
                    row = (source_plate_id, source_well, seq_plate_number,
                           seq_well)
                    process_legacy_row(row, all_recorded_sequences,
                                       seq_well_to_tube)


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
    else:
        legacy_clone = None
        legacy_tracking = None

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
