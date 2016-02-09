import argparse
import csv
import glob
import os.path
import xlrd

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from library.models import LibrarySequencing
from utils.scripting import require_db_write_acknowledgement


class Command(BaseCommand):
    """
    Command to import sequencing data.

    Arguments

    - tracking_numbers is a csv with header row, containing the genewiz
      orders to be added. Three columns are needed, in any order:
      `order_date`, `tracking_number`, and `seq_plate_name`.
      These files currently live in:

          materials/sequencing/tracking_numbers

    - genewiz_output_root is the root directory where Genewiz dumps our
      sequencing data. Inside this directory are several Perl
      scripts that Huey-Ling used to make the Genewiz output more
      convenient to parse. The only one of these Perl scripts that is
      required to have been run before using this command is
      rmDateFromSeqAB1.pl, which removes the date from certain
      filenames. Otherwise, this script is flexible about dealing with
      Genewiz's Excel format, or Huey-Ling's text file format.
      This directory currently lives at:

          materials/sequencing/genewiz_dump/genewiz_data

    - cherrypick_list is a csv with header row, listing which library
      stocks correspond to which sequencing wells. It should be in
      standard cherrypick list format, i.e., with four columns:
      `source_plate`, `source_well`, `destination_plate`, and
      `destination_well`. In this case, "source" is the library stock,
      and "destination" is the sequencing plate. E.g., if
      universal-F1_A12 was picked into sequencing plate JL42, well B09,
      the row would look like:

          universal-F1,A12,JL42,B09

      These files currently live in:

          materials/sequencing/cherrypick_lists

    """

    help = 'Import sequencing data (from 2014-on)'

    def add_arguments(self, parser):
        parser.add_argument('tracking_numbers',
                            type=argparse.FileType('r'),
                            help="CSV of Genewiz tracking numbers. "
                                 "See this command's docstring "
                                 "for more details.")

        parser.add_argument('genewiz_output_root',
                            help="Root Genewiz output directory. "
                                 "See this command's docstring "
                                 "for more details.")

    def handle(self, **options):
        require_db_write_acknowledgement()

        tracking_numbers = options['tracking_numbers']
        genewiz_root = options['genewiz_output_root']

        if not os.path.isdir(genewiz_root):
            raise CommandError('genewiz_root directory not found')

        ###################################
        # FIRST STAGE: Add raw genewiz data
        #   (sequences and quality scores)
        ###################################

        reader = csv.DictReader(tracking_numbers)

        for row in reader:
            tracking_number = row['tracking_number'].strip()
            order_date = row['order_date'].strip()
            process_tracking_number(tracking_number, order_date,
                                    genewiz_root)

        ##################################################
        # SECOND STAGE: Add source information
        #   (which library stocks go with which sequences)
        ##################################################

        # TODO: here I should iterate over the CSV saying
        # which seq wells correspond to which library wells


def process_tracking_number(tracking_number, order_date, genewiz_root):
    """
    Process all the rows for a particular Genewiz tracking number.

    A Genewiz tracking number corresponds to one sequencing plate.
    """
    qscrl_txt = ('{}/{}_qscrl.txt'.format(genewiz_root, tracking_number))
    qscrl_xls = ('{}/{}_qscrl.xls'.format(genewiz_root, tracking_number))

    # First try .txt file (HueyLing converted some but not all to .txt)
    try:
        qscrl_file = open(qscrl_txt, 'rb')
        with qscrl_file:
            qscrl_reader = csv.DictReader(qscrl_file, delimiter='\t')
            for row in qscrl_reader:
                # need tracking number and tube label because they are the
                # fields that genewiz uses to uniquely define sequences,
                # in the case of resequencing.
                _process_qscrl_row(
                    row, tracking_number, order_date, genewiz_root)

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

                _process_qscrl_row(
                    row, tracking_number, order_date, genewiz_root)

        # If neither .txt or .xls file, error
        except IOError as e:
            raise CommandError(
                'QSCRL file missing or could not be open for '
                'tracking number {}. I/O error({}): {}\n'
                .format(tracking_number, e.errno, e.strerror))


def _process_qscrl_row(row, tracking_number, order_date, genewiz_root):
    """
    Process a row from a Genewiz QSCRL file.

    sample_plate_name and sample_tube_number are needed because they
    are how we label our samples and record what sample came from
    which library stocks.

    Note that tube_label can't be used for sample_tube_number
    because it is often 1-2 instead of 95-96, if genewiz splits
    the order into two plates.

    Also, avoid Template_Name... sometimes e.g. 'GC1'
    """
    if tracking_number != row['trackingNumber']:
        raise CommandError('TrackingNumber mismatch between filename & '
                           'QSCRL row for {}'.format(tracking_number))

    tube_label = row['TubeLabel']
    pk = tracking_number + '_' + tube_label
    dna_name = row['DNAName']
    sample_plate_name = _get_plate_name_from_dna_name(dna_name)
    sample_tube_number = _get_tube_number_from_dna_name(dna_name)

    if '_R' in tube_label:
        dna_name += '_R'

    seq_filepath = ('{}/{}_seq/{}_*.seq'.format(
        genewiz_root, tracking_number, dna_name))

    try:
        seq_file = open(glob.glob(seq_filepath)[0], 'rb')

    except IOError:
        raise CommandError('Seq file missing for tracking {}, dna {}\n'
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
            pk=pk,
            sample_plate_name=sample_plate_name,
            sample_tube_number=sample_tube_number,
            genewiz_order_date=order_date,
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


def add_source(seq_plate, seq_well, library_stock):
    """
    For all sequences corresponding to seq_plate and seq_well,
    add library_stock as the source.

    Note that there might be multiple sequences in the database
    corresponding to the same sequencing sample. This is because
    Genewiz sometimes re-sequences samples with bad results.
    """
    seq_tube_number = _seq_well_to_seq_tube_number(seq_well)

    sequences = LibrarySequencing.objects.filter(
        sample_plate_name=seq_plate, sample_tube_number=seq_tube_number)

    if not sequences:
        raise CommandError('No sequences in database for {} {}\n'
                           .format(seq_plate, seq_tube_number))

    for sequence in sequences:
        sequence.source_stock = library_stock
        sequence.save()


def _seq_well_to_seq_tube_number(seq_well):
    """
    Translate from seq well to seq tube number.

    The pattern is:
    (A01, B01, C01, ..., H01) => (1, 2, 3, ..., 8)
    (A02, B02, C02, ..., H02) => (9, 10, 11, ..., 16)
    ...
    (A12, B12, C12, ..., H12) => (89, 90, 91, ..., 96)
    """
    row = ord(seq_well[0]) - 64  # 1-indexed
    col = int(seq_well[1:]) - 1  # 0-indexed
    return row + (8 * col)


def _get_plate_name_from_dna_name(dna_name):
    """Extract plate name from genewiz dna name"""
    return dna_name.split('_')[0]


def _get_tube_number_from_dna_name(dna_name):
    """Extract tube number from genewiz dna name"""
    try:
        return int(dna_name.split('_')[1].split('-')[0])
    except ValueError:
        raise ValueError('dna_name {} parsed with a non-int tube number'
                         .format(dna_name))
