import argparse
import csv
import glob
import MySQLdb
import os.path
import xlrd

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from dbmigration.helpers.object_getters import get_library_stock
from eegi.local_settings import LEGACY_DATABASE
from library.models import LibraryStock, LibrarySequencing
from utils.scripting import require_db_write_acknowledgement
from utils.wells import get_well_name


class Command(BaseCommand):
    """
    Command to import SUP Secondary sequencing data.

    Imports this from both the legacy database and from Genewiz output files.

    This script requires that LEGACY_DATABASE be defined in
    local_settings.py.

    Arguments

    - tracking_numbers is a csv dump of the Google Doc in which we
      kept track of our Genewiz tracking numbers, necessary so that this
      command skips Genewiz data unrelated to the GI screen. This file
      currently lives at:

          materials/sequencing/genewiz/tracking_numbers.csv

    - genewiz_output_root is the root directory where Genewiz dumps our
      sequencing data. Inside this directory are several Perl
      scripts that Huey-Ling used to make the Genewiz output more
      convenient to parse. The only one of these Perl scripts that is
      required to have been run before using this command is
      rmDateFromSeqAB1.pl, which removes the date from certain
      filenames. Otherwise, this script is flexible about dealing with
      Genewiz's Excel format, or Huey-Ling's text file format.
      This directory currently lives at:

          materials/sequencing/genewiz/genewiz_data
    """

    help = 'Import sequencing data from Genewiz output files'

    def add_arguments(self, parser):
        parser.add_argument('tracking_numbers', type=argparse.FileType('r'),
                            help="CSV of Genewiz tracking numbers. "
                                 "See this command's docstring "
                                 "for more details.")

        parser.add_argument('genewiz_output_root',
                            help="Root Genewiz output directory. "
                                 "See this command's docstring "
                                 "for more details.")

    def handle(self, **options):
        tracking_numbers = options['tracking_numbers']
        self.genewiz_root = options['genewiz_output_root']

        if not os.path.isdir(self.genewiz_root):
            raise CommandError('genewiz_root directory not found')

        require_db_write_acknowledgement()

        legacy_db = MySQLdb.connect(host=LEGACY_DATABASE['HOST'],
                                    user=LEGACY_DATABASE['USER'],
                                    passwd=LEGACY_DATABASE['PASSWORD'],
                                    db=LEGACY_DATABASE['NAME'])
        cursor = legacy_db.cursor()

        ######################################################
        # FIRST STAGE
        #
        #   Add raw genewiz data (sequence and quality scores)
        #
        ######################################################

        reader = csv.DictReader(tracking_numbers)

        for row in reader:
            tracking_number = row['tracking_number'].strip()
            self._process_tracking_number(tracking_number)

        ######################################
        # SECOND STAGE
        #
        #   Add source LibraryStock information
        #
        ######################################

        self.sequences = LibrarySequencing.objects.all()

        # Create a dictionary to translate from sequencing well to tube number
        #   (use SeqPlateID=1 because it happens to have all 96 wells)
        cursor.execute('SELECT tubeNum, Seq96well FROM SeqPlate '
                       'WHERE SeqPlateID=1')

        self.seq_well_to_tube = {}
        for row in cursor.fetchall():
            self.seq_well_to_tube[row[1]] = row[0]

        # Process source information for plates 1-56
        #   (from the legacy database)
        legacy_query = ('SELECT RNAiPlateID, 96well, SeqPlateID, Seq96Well, '
                        'oriClone, receiptID FROM SeqPlate')
        cursor.execute(legacy_query)
        legacy_rows = cursor.fetchall()

        for row in legacy_rows:
            try:
                source_stock = get_library_stock(row[0], row[1])

            except ObjectDoesNotExist:
                raise CommandError('LibraryStock not found for {} {}\n'
                                   .format(row[0], row[1]))

            self._process_source_information(source_stock, row[2],
                                             row[3], row[4], row[5])

        # Process source information for plates 57-66
        #   (these are NOT in legacy database; entire plate sequenced)
        full_seq_plates = {
            57: 'hybrid-F1', 58: 'hybrid-F2', 59: 'hybrid-F3',
            60: 'hybrid-F4', 61: 'hybrid-F5', 62: 'hybrid-F6',
            63: 'universal-F5', 64: 'or346-F6', 65: 'or346-F7', 66: 'mr17-F3',
        }

        for seq_plate_number in full_seq_plates:
            source_plate_id = full_seq_plates[seq_plate_number]
            library_stocks = LibraryStock.objects.filter(plate=source_plate_id)

            for library_stock in library_stocks:
                self._process_source_information(
                    library_stock, seq_plate_number, library_stock.well)

        # Process plates 67-on
        #   (these are NOT in legacy database, and only some columns sequenced)
        full_seq_columns = {
            67: {
                1: ('hc69-F7', 1),
                2: ('hc69-F7', 3),
                3: ('hc69-F7', 4),
                4: ('hc69-F7', 5),
                5: ('g53-F2', 8),
                6: ('g53-F2', 9),
                7: ('g53-F2', 10),
                8: ('it5-F3', 4, 'DEFGH'),
                9: ('it5-F3', 5),
                10: ('it57-F4', 4, 'GH'),
                11: ('ye60-F2', 8),
                12: ('b244-F1', 12),
            },
            68: {
                1: ('or191-F1', 1),
                2: ('or191-F1', 3),
                3: ('or191-F1', 4),
                4: ('or191-F1', 5),
                5: ('or191-F1', 6),
                6: ('or191-F1', 8),
                7: ('or191-F1', 9),
                8: ('or191-F1', 10),
                9: ('or191-F1', 12),
                10: ('or191-F2', 1),
                11: ('or191-F2', 3),
                12: ('or191-F2', 4),
            },
            69: {
                1: ('or191-F2', 5),
                2: ('or191-F2', 6),
                3: ('or191-F2', 8),
                4: ('or191-F2', 9),
                5: ('or191-F2', 10),
                6: ('or191-F2', 12),
                7: ('or191-F3', 1),
                8: ('or191-F3', 3),
                9: ('b235-F5', 1),
                10: ('b235-F5', 3),
                11: ('b235-F5', 4),
                12: ('b235-F5', 5),
            },
            70: {
                1: ('b235-F5', 6),
                2: ('b235-F5', 8),
                3: ('b235-F5', 9),
                4: ('b235-F5', 10),
                5: ('b235-F5', 12),
                6: ('b235-F6', 1),
                7: ('b235-F6', 3),
                8: ('b235-F6', 4),
                9: ('b235-F6', 5),
                10: ('b235-F6', 6),
                11: ('b235-F6', 8),
                12: ('b235-F6', 9),
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
                    source_stock = get_library_stock(
                        source_plate_id, source_well)

                    self._process_source_information(
                        source_stock, seq_plate_number, seq_well)

    def _process_tracking_number(self, tracking_number):
        """
        Process all the rows for a particular Genewiz tracking number.

        A Genewiz tracking number corresponds to one sequencing plate.
        """
        qscrl_txt = ('{}/{}_qscrl.txt'.format(self.genewiz_root,
                                              tracking_number))
        qscrl_xls = ('{}/{}_qscrl.xls'.format(self.genewiz_root,
                                              tracking_number))
        # First try .txt file
        try:
            qscrl_file = open(qscrl_txt, 'rb')
            with qscrl_file:
                qscrl_reader = csv.DictReader(qscrl_file, delimiter='\t')
                for row in qscrl_reader:
                    # need tracking number and tube label because they are the
                    # fields that genewiz uses to uniquely define sequences,
                    # in the case of resequencing.
                    self._process_qscrl_row(row)

        # If .txt file does not work, try .xls
        except IOError:
            try:
                book = xlrd.open_workbook(qscrl_xls, on_demand=True)
                sheet = book.sheet_by_name(tracking_number)
                keys = [sheet.cell(4, col_index).value
                        for col_index in xrange(sheet.ncols)]
                for row_index in xrange(5, sheet.nrows):
                    row = {}
                    for col_index in xrange(sheet.ncols):
                        cell_value = sheet.cell_value(row_index, col_index)
                        row[keys[col_index]] = cell_value

                    self._process_qscrl_row(row)

            # If neither .txt or .xls file, error
            except IOError as e:
                raise CommandError(
                    'QSCRL file missing or could not be open for '
                    'tracking number {}. I/O error({}): {}\n'
                    .format(tracking_number, e.errno, e.strerror))

    def _process_qscrl_row(self, row):
        """
        Process a row of QSCRL information.

        Need sample_plate_name and sample_tube_number because they are
        how we label our samples (to identify what sequence well came
        from what library well).

        Note that tube_label can't be used for sample_tube_number
        because it is often 1-2 instead of 95-96

        Also, avoid Template_Name... sometimes e.g. 'GC1'
        """
        tracking_number = row['trackingNumber']
        tube_label = row['TubeLabel']
        dna_name = row['DNAName']
        sample_plate_name = _get_plate_name_from_dna_name(dna_name)
        sample_tube_number = _get_tube_number_from_dna_name(dna_name)

        if '_R' in tube_label:
            dna_name += '_R'

        seq_filepath = ('{}/{}_seq/{}_*.seq'.format(self.genewiz_root,
                                                    tracking_number,
                                                    dna_name))
        try:
            seq_file = open(glob.glob(seq_filepath)[0], 'rb')

        except IOError:
            raise CommandError('Seq file missing for tracking number '
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
                si_t=row['SI_T'])

            new_sequence.save()

    def _process_source_information(self, source_stock,
                                    seq_plate_number, seq_well,
                                    legacy_clone=None, legacy_tracking=None):
        """
        Process the source information for a sequencing sample.

        source_stock is the library stock that was sequenced.

        seq_plate_number and seq_well are identifying information re:
        the sequencing plate/tube that was sent off to Genewiz.
        """
        # Sanity check that clone matches
        if legacy_clone:
            clone = source_stock.intended_clone
            if (not clone or (legacy_clone != clone.id and
                              'GHR' not in clone.id)):
                self.stderr.write(
                    'ERROR: Clone mismatch for {}: {} {}\n'
                    .format(source_stock, clone, legacy_clone))

        seq_plate_name = 'JL' + str(seq_plate_number)
        seq_tube_number = self.seq_well_to_tube[seq_well]

        sequences = self.sequences.filter(sample_plate_name=seq_plate_name,
                                          sample_tube_number=seq_tube_number)

        if not sequences:
            raise CommandError('No record in database for sequencing '
                               'record {} {}\n'.format(seq_plate_name,
                                                       seq_tube_number))

        for sequence in sequences:
            # Sanity check for tracking number match
            if (legacy_tracking and
                    legacy_tracking != sequence.genewiz_tracking_number):
                raise CommandError('Tracking number mismatch for sequencing '
                                   'record {}\n'.format(sequence))

            sequence.source_stock = source_stock
            sequence.save()


def _get_plate_name_from_dna_name(dna_name):
    return dna_name.split('_')[0]


def _get_tube_number_from_dna_name(dna_name):
    try:
        return int(dna_name.split('_')[1].split('-')[0])
    except ValueError:
        raise ValueError('dna_name {} parsed with a non-int tube number'
                         .format(dna_name))
