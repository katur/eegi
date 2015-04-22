import argparse
import csv
import glob
import MySQLdb
import os.path
import xlrd

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from eegi.local_settings import LEGACY_DATABASE
from library.helpers.well_naming import get_well_name
from library.models import LibraryWell, LibrarySequencing
from utils.helpers.scripting import require_db_write_acknowledgement

HELP = '''
Sync the sequencing data from the Genewiz output files to the database.

This script requires that LEGACY_DATABASE be defined in local_settings.py,
to connect to the GenomeWideGI legacy database.

tracking_numbers should be a csv dump of the Google Doc in which we
kept track of our Genewiz tracking numbers, which is necessary so that this
script examines only the GI data (and not data from Genewiz for other lab
members). This file currently lives at:

   materials/sequencing/genewiz/tracking_numbers.csv

genewiz_root should be the root of a directory containing the Genewiz
output. Inside that directory are several Perl scripts that HueyLing used
to make the Genewiz output more convenient to parse. The only one of
these Perl scripts that is required to have been run before using this script
is rmDateFromSeqAB1.pl, which removes the date from certain filenames.
Otherwise, this script is flexible about dealing with Genewiz's Excel
format, or Huey-Ling's text file format. This directory currently lives at:

    materials/sequencing/genewiz/genewiz_data

'''


class Command(BaseCommand):
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('tracking_numbers', type=argparse.FileType('r'))
        parser.add_argument('genewiz_root')

    def handle(self, **options):
        tracking_numbers = options['tracking_numbers']
        self.genewiz_root = options['genewiz_root']
        if not os.path.isdir(self.genewiz_root):
            raise CommandError('genewiz_root directory not found')

        require_db_write_acknowledgement()

        legacy_db = MySQLdb.connect(host=LEGACY_DATABASE['HOST'],
                                    user=LEGACY_DATABASE['USER'],
                                    passwd=LEGACY_DATABASE['PASSWORD'],
                                    db=LEGACY_DATABASE['NAME'])
        cursor = legacy_db.cursor()

        # Add raw genewiz data to database (sequence and quality scores).
        # Use tracking_numbers to limit to GI sequences only
        # (as opposed to sequences for other lab members)
        reader = csv.DictReader(tracking_numbers)

        for row in reader:
            tracking_number = row['tracking_number'].strip()
            self.process_tracking_number(tracking_number)

        # Retrieve all the sequencing objects just recorded
        self.sequences = LibrarySequencing.objects.all()

        # Create a dictionary to translate from sequencing well to tube number
        # (choose SeqPlateID=1 because it happens to have all 96 wells)
        cursor.execute('SELECT tubeNum, Seq96well FROM SeqPlate '
                       'WHERE SeqPlateID=1')
        self.seq_well_to_tube = {}
        for row in cursor.fetchall():
            self.seq_well_to_tube[row[1]] = row[0]

        # Process source information for plates 1-56
        # (from the legacy database)
        legacy_query = ('SELECT RNAiPlateID, 96well, SeqPlateID, Seq96Well, '
                        'oriClone, receiptID FROM SeqPlate')
        cursor.execute(legacy_query)
        legacy_rows = cursor.fetchall()

        for row in legacy_rows:
            self.process_source_information(row)

        # Process source information plates 57-66
        # (not in legacy database; entire plate sequenced)
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
                self.process_source_information(row)

        # Process plates 67-on
        # (not in legacy database; only certain columns sequenced)
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
                    self.process_source_information(row)

    def process_tracking_number(self, tracking_number):
        qscrl_txt = ('{}/{}_qscrl.txt'.format(self.genewiz_root,
                                              tracking_number))
        qscrl_xls = ('{}/{}_qscrl.xls'.format(self.genewiz_root,
                                              tracking_number))
        try:
            qscrl_file = open(qscrl_txt, 'rb')
            with qscrl_file:
                qscrl_reader = csv.DictReader(qscrl_file, delimiter='\t')
                for row in qscrl_reader:
                    # need tracking number and tube label because they are the
                    # fields that genewiz uses to uniquely define sequences,
                    # in the case of resequencing.
                    self.process_qscrl_row(row)

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

                    self.process_qscrl_row(row)

            except IOError as e:
                self.stderr.write('QSCRL file missing or could not be open '
                                  'for tracking number {}. I/O error({}): {}\n'
                                  .format(tracking_number, e.errno,
                                          e.strerror))
                return

    def process_qscrl_row(self, row):
        '''
        Process a row of QSCRL information.

        Need sample_plate_name and sample_tube_number because they are
        how we label our samples (to identify what sequence well came
        from what library well).

        Note that tube_label can't be used for sample_tube_number
        because it is often 1-2 instead of 95-96

        Also, avoid Template_Name... sometimes e.g. 'GC1'

        '''

        tracking_number = row['trackingNumber']
        tube_label = row['TubeLabel']
        dna_name = row['DNAName']
        sample_plate_name = get_plate_name_from_dna_name(dna_name)
        sample_tube_number = get_tube_number_from_dna_name(dna_name)

        if '_R' in tube_label:
            dna_name += '_R'

        seq_filepath = ('{}/{}_seq/{}_*.seq'.format(self.genewiz_root,
                                                    tracking_number,
                                                    dna_name))
        try:
            seq_file = open(glob.glob(seq_filepath)[0], 'rb')

        except IOError:
            self.stderr.write('Seq file missing for tracking number '
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

    def process_source_information(self, row):
        # The plate and well that the sequencing result came from
        source_plate_id = row[0]
        source_well = row[1]

        # Identifying information for the plate/tube that were sequenced
        sample_plate_name = 'JL' + str(row[2])
        sample_well = row[3]
        sample_tube_number = self.seq_well_to_tube[sample_well]

        # Legacy clone and legacy tracking just for double checking
        if len(row) > 4:
            legacy_clone = row[4]
            legacy_tracking = row[5]
        else:
            legacy_clone = None
            legacy_tracking = None

        sequences = self.sequences.filter(
            sample_plate_name=sample_plate_name,
            sample_tube_number=sample_tube_number)

        if not sequences:
            self.stderr.write('No record in new database for sequencing '
                              'record {} {}\n'.format(sample_plate_name,
                                                      sample_tube_number))
        else:
            for sequence in sequences:
                if (legacy_tracking and
                        legacy_tracking != sequence.genewiz_tracking_number):
                    self.stderr.write('Tracking number mismatch for '
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
                            self.stderr.write(
                                'Clone mismatch for {} {}: {} {}\n'
                                .format(source_plate_id, source_well,
                                        clone, legacy_clone))

                    except AttributeError:
                        # Due to a few cases of no intended clone
                        # being sequenced
                        self.stderr.write('LibraryWell {} has no intended '
                                          'clone\n'
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
                    self.stderr.write('LibraryWell {} not found\n'
                                      .format(source_library_well_id))


def get_plate_name_from_dna_name(dna_name):
    return dna_name.split('_')[0]


def get_tube_number_from_dna_name(dna_name):
    try:
        return int(dna_name.split('_')[1].split('-')[0])
    except ValueError:
        raise ValueError('dna_name {} parsed with a non-int tube number'
                         .format(dna_name))
