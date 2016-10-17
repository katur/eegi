import argparse
import csv
import glob
import os.path
import xlrd

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from library.models import LibrarySequencing, LibraryStock
from utils.scripting import require_db_write_acknowledgement


class Command(BaseCommand):
    """
    Command to import sequencing data.

    Arguments:

    - cherrypick_list is a csv, including header row, listing which library
      stocks correspond to which sequencing wells. It should be in
      standard cherrypick list format, i.e., with four columns:
      `source_plate`, `source_well`, `destination_plate`, and
      `destination_well`. In this case, "source" is the library stock,
      and "destination" is the sequencing plate. E.g., if
      universal-F1_A12 was picked into sequencing plate JL42, well B09,
      the row would look like `universal-F1,A12,JL42,B09`.

    - tracking_numbers is a csv, including header row, containing the genewiz
      orders to be added. Two columns are needed, in any order:
      `order_date` and `tracking_number`. Tracking numbers are typically
      stored in the `Genetic Interactions/Sequencing` Google Drive share (and
      can be exported from there).

    - genewiz_output_root is the root directory where Genewiz dumps our
      sequencing data. Inside this directory are several Perl
      scripts that Huey-Ling used to make the Genewiz output more
      convenient to parse. The only one of these Perl scripts that is
      required to have been run before using this command is
      rmDateFromSeqAB1.pl, which removes the date from certain
      filenames. Otherwise, this script is flexible about dealing with
      Genewiz's Excel format, or Huey-Ling's text file format.

    *** NOTE TO ALAN ***:
    Genewiz is currently dumping our data to pleaides, but the project is now
    deployed on pyxis. When Katherine ran this script (which she only had to do
    once), the project was not yet deployed, so she simply rsynced the
    sequencing data from pleiades to her own devbox. Going forward, you'll want
    to import new sequencing data to the production database, so should modify
    this script to read from the live Genewiz dump.
    """

    help = 'Import sequencing data (from 2014-on)'

    def add_arguments(self, parser):
        parser.add_argument('cherrypick_list',
                            type=argparse.FileType('r'),
                            help="CSV of cherrypick list. "
                                 "See this command's docstring "
                                 "for more details.")

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

        cherrypick_list = options['cherrypick_list']
        tracking_numbers = options['tracking_numbers']
        genewiz_root = options['genewiz_output_root']

        if not os.path.isdir(genewiz_root):
            raise CommandError('genewiz_root directory not found')

        ####################################################
        # FIRST STAGE: Create a mapping of sequencing result
        #   to library stock, using the cherrypick_list
        #   input file.
        ####################################################

        seq_to_source = {}

        reader = csv.DictReader(cherrypick_list)

        for row in reader:
            source_plate = row['source_plate'].strip()

            # skip empty lines
            if not source_plate:
                continue

            source_well = row['source_well'].strip()
            library_stock = LibraryStock.objects.get(
                plate_id=source_plate, well=source_well)

            seq_plate = row['destination_plate'].strip()
            seq_well = row['destination_well'].strip()
            key = seq_plate + '_' + seq_well

            seq_to_source[key] = library_stock

        #######################################################
        # SECOND STAGE: Add sequencing results (sequences plus
        #   quality scores) to the database, for all tracking
        #   numbers listed in the tracking_numbers input file.
        #   Use the mapping from FIRST STAGE to create the
        #   pointers to LibraryStock.
        #######################################################

        reader = csv.DictReader(tracking_numbers)

        for row in reader:
            tracking_number = row['tracking_number'].strip()
            order_date = row['order_date'].strip()
            process_tracking_number(tracking_number, order_date,
                                    genewiz_root, seq_to_source)


def process_tracking_number(tracking_number, order_date, genewiz_root,
                            seq_to_source):
    """
    Process all the rows for a particular Genewiz tracking number.

    Arguments
        - the tracking_number and order_date, supplied by Genewiz. You
          can find these in our Genewiz account after Genewiz receives
          and processes an order.
        - the root of the directory where Genewiz dumps the sequencing
          output. See command-level docstring for more details.
        - seq_to_source is a dictionary mapping sequencing wells to
          the library stocks they came from. Keys should be in format
          seqplate_seqwell, e.g., "JL71_B09".
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
                _process_qscrl_row(row, tracking_number, order_date,
                                   genewiz_root, seq_to_source)

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

                _process_qscrl_row(row, tracking_number, order_date,
                                   genewiz_root, seq_to_source)

        # If neither .txt or .xls file, error
        except IOError as e:
            raise CommandError(
                'QSCRL file missing or could not be open for '
                'tracking number {}. I/O error({}): {}\n'
                .format(tracking_number, e.errno, e.strerror))


def _process_qscrl_row(row, tracking_number, order_date, genewiz_root,
                       seq_to_source):
    """
    Process a row from a Genewiz QSCRL file.

    Avoid using the Genewiz `Template_Name` field, since it does not
    always correspond to our sample plate name (e.g. 'GC1')
    """
    if tracking_number != row['trackingNumber']:
        raise CommandError('TrackingNumber mismatch between filename & '
                           'QSCRL row for {}'.format(tracking_number))

    tube_label = row['TubeLabel']
    pk = tracking_number + '_' + tube_label
    dna_name = row['DNAName']
    seq_plate = _get_plate_name_from_dna_name(dna_name)
    seq_tube_number = _get_tube_number_from_dna_name(dna_name)
    seq_well = _seq_tube_number_to_well(seq_tube_number)

    try:
        key = seq_plate + '_' + seq_well
        library_stock = seq_to_source[key]
    except KeyError:
        library_stock = None

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

    # TODO: decide whether this script should update the other fields if this
    # sequencing result already exists.
    try:
        LibrarySequencing.objects.get(
            genewiz_tracking_number=tracking_number,
            genewiz_tube_label=tube_label)

    except ObjectDoesNotExist:
        new_sequence = LibrarySequencing(
            pk=pk,
            sample_plate=seq_plate,
            sample_well=seq_well,
            sample_tube_number=seq_tube_number,
            source_stock=library_stock,
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


def _seq_tube_number_to_well(seq_tube_number):
    """
    Translate from seq tube number to well.

    The pattern is:
    (1, 2, 3, ..., 8) => (A01, B01, C01, ..., H01)
    (9, 10, 11, ..., 16) => (A02, B02, C02, ..., H02)
    ...
    (89, 90, 91, ..., 96) => (A12, B12, C12, ..., H12)
    """
    seq_tube_number -= 1  # make it 0-indexed

    quotient = seq_tube_number // 8
    remainder = seq_tube_number % 8

    row = chr(remainder + 65)
    col = str(quotient + 1).zfill(2)

    return row + col


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
