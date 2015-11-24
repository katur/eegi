"""This module contains the steps for the sync_legacy_database command
that involve the library and clones apps.

"""
import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError

from clones.models import Clone
from library.models import LibraryPlate, LibraryStock

from dbmigration.helpers.name_getters import (
    get_ahringer_384_plate_name, get_vidal_clone_name,
    get_library_stock_name, get_library_plate_name)

from dbmigration.helpers.object_getters import (
    get_clone, get_library_stock, get_library_plate)

from dbmigration.helpers.sync_helpers import sync_rows, update_or_save_object

from utils.wells import get_three_character_well


def update_Clone_table(command, cursor):
    """Update the Clone table with distinct clones from legacy table
    RNAiPlate.

    Find the distinct Ahringer clone names (in 'sjj_X' format) and
    the L4440 empty vector clone (just called 'L4440')
    from the clone field of RNAiPlate.

    Find the distinct Vidal clone names (in 'GHR-X@X' format)
    from the 384PlateID and 384Well fields of RNAiPlate
    (note that we are no longer using the 'mv_X'-style Vidal clone names,
    and our PK for Vidal clones will now be in 'GHR-X@X' style).

    """
    recorded_clones = Clone.objects.all()
    fields_to_compare = None

    legacy_query = ('SELECT DISTINCT clone FROM RNAiPlate '
                    'WHERE clone LIKE "sjj%" OR clone = "L4440"')

    def sync_clone_row(legacy_row):
        new_clone = Clone(id=legacy_row[0])
        return update_or_save_object(command, new_clone, recorded_clones,
                                     fields_to_compare)

    legacy_query_vidal = ('SELECT DISTINCT 384PlateID, 384Well FROM RNAiPlate '
                          'WHERE clone LIKE "mv%"')

    def sync_clone_row_vidal(legacy_row):
        vidal_clone_name = get_vidal_clone_name(legacy_row[0], legacy_row[1])
        new_clone = Clone(id=vidal_clone_name)
        return update_or_save_object(command, new_clone, recorded_clones,
                                     fields_to_compare)

    sync_rows(command, cursor, legacy_query, sync_clone_row)
    sync_rows(command, cursor, legacy_query_vidal, sync_clone_row_vidal)


def update_LibraryPlate_table(command, cursor):
    """Update LibraryPlate table with distinct plates in legacy tables
    RNAiPlate and CherryPickRNAiPlate.

    Find original Ahringer 384-well plates through the chromosome and
    384PlateID fields of RNAiPlate (384PlateID NOT LIKE GHR-%, != 0).

    Find original Orfeome plates through the 384PlateID field of RNAiPlate
    (384PlateID LIKE GHR-%). Note that these original Orfeome plates
    are actually in 96-well format.

    Find the plates actually used in our primary experiments as the
    distinct RNAiPlateID from RNAiPlate, and the distinct RNAiPlateID
    LIKE Eliana% from ReArrayRNAiPlate.

    Find the plates actually used in our secondary experiments as the
    distinct RNAiPlateID from CherryPickRNAiPlates. Must also skip L4440
    (because in order to get around some bizarities in the old database
    separating the primary and secondary screens into two tables, we have
    the same L4440 plate listed in both tables in the legacy database).

    """
    recorded_plates = LibraryPlate.objects.all()
    fields_to_compare = ('screen_stage', 'number_of_wells')

    legacy_query_384_plates = ('SELECT DISTINCT chromosome, 384PlateID '
                               'FROM RNAiPlate '
                               'WHERE 384PlateID NOT LIKE "GHR-%" '
                               'AND 384PlateID != 0')

    legacy_query_orfeome_plates = ('SELECT DISTINCT 384PlateID '
                                   'FROM RNAiPlate '
                                   'WHERE 384PlateID LIKE "GHR-%"')

    legacy_query_l4440_plate = ('SELECT DISTINCT RNAiPlateID '
                                'FROM RNAiPlate '
                                'WHERE RNAiPlateID = "L4440"')

    legacy_query_primary_plates = ('SELECT DISTINCT RNAiPlateID '
                                   'FROM RNAiPlate '
                                   'WHERE RNAiPlateID != "L4440"')

    legacy_query_eliana_rearrays = ('SELECT DISTINCT RNAiPlateID FROM '
                                    'ReArrayRNAiPlate WHERE RNAiPlateID '
                                    'LIKE "Eliana%"')

    legacy_query_secondary_plates = ('SELECT DISTINCT RNAiPlateID '
                                     'FROM CherryPickRNAiPlate '
                                     'WHERE RNAiPlateID != "L4440"')

    def sync_library_plate_row(legacy_row, screen_stage=None,
                               number_of_wells=96):
        if len(legacy_row) > 1:
            plate_name = get_ahringer_384_plate_name(legacy_row[0],
                                                     legacy_row[1])
        else:
            plate_name = get_library_plate_name(legacy_row[0])

        new_plate = LibraryPlate(id=plate_name, screen_stage=screen_stage,
                                 number_of_wells=number_of_wells)

        return update_or_save_object(command, new_plate, recorded_plates,
                                     fields_to_compare)

    # Sync the 384-well Ahringer plates from which our 96-well Ahringer plates
    # were arrayed
    sync_rows(command, cursor, legacy_query_384_plates,
              sync_library_plate_row, screen_stage=0,
              number_of_wells=384)

    # Sync the 96-well Orfeome plates from which our 96-well Vidal rearrays
    # were cherry-picked
    sync_rows(command, cursor, legacy_query_orfeome_plates,
              sync_library_plate_row, screen_stage=0)

    # Sync the L4440 plate used in both Primary and Seconday experiments
    sync_rows(command, cursor, legacy_query_l4440_plate,
              sync_library_plate_row)

    # Sync the 96-well plates used in our Primary experiments (includes
    # Ahringer plates and Vidal plates)
    sync_rows(command, cursor, legacy_query_primary_plates,
              sync_library_plate_row, screen_stage=1)

    # Sync the 96-well "Eliana Rearray" plates, which tried to salvage wells
    # that did not grow consistently in the other primary screen plates
    sync_rows(command, cursor, legacy_query_eliana_rearrays,
              sync_library_plate_row, screen_stage=1)

    # Sync the 96-well plates used for our Secondary experiments
    sync_rows(command, cursor, legacy_query_secondary_plates,
              sync_library_plate_row, screen_stage=2)


def update_LibraryStock_table(command, cursor):
    """Update the LibraryStock table to reflect the clone layout of all plates:
    source plates (Ahringer 384 and original Orfeome plates e.g. GHR-10001),
    primary plates, and secondary plates. Also update the parent LibraryStocks
    of primary and secondary plates.

    This information comes from a variety of queries of
    primarily according to legacy tables RNAiPlate and CherryPickRNAiPlate.
    Detailed comments inline.

    """
    recorded_wells = LibraryStock.objects.all()
    fields_to_compare = ('plate', 'well', 'parent_stock',
                         'intended_clone')

    # 'Source' plates are Ahringer 384 plates and original Orfeome
    # plates (e.g. GHR-10001). Plate names are captured as they
    # were in update_LibraryPlate_table (i.e., using fields 384PlateID and
    # chromosome). Well is captured in field 384Well. Clone is captured
    # as described in update_Clone_table (i.e., using clone field for
    # sjj clones, and source plate@well for mv clones).
    legacy_query_source = ('SELECT DISTINCT 384PlateID, 384Well, '
                           'chromosome, clone FROM RNAiPlate '
                           'WHERE clone LIKE "sjj%" OR clone LIKE "mv%"')

    def sync_source_row(legacy_row):
        plate_name = legacy_row[0]
        clone_name = legacy_row[3]

        if re.match('sjj', clone_name):
            chromosome = legacy_row[2]
            plate_name = get_ahringer_384_plate_name(chromosome, plate_name)

        well_improper = legacy_row[1]
        well_proper = get_three_character_well(well_improper)

        if re.match('mv', clone_name):
            clone_name = get_vidal_clone_name(plate_name, well_improper)

        new_well = LibraryStock(
            id=get_library_stock_name(plate_name, well_proper),
            plate=get_library_plate(plate_name), well=well_proper,
            parent_stock=None, intended_clone=get_clone(clone_name))

        return update_or_save_object(command, new_well, recorded_wells,
                                     fields_to_compare)

    # Primary well layout captured in RNAiPlate table (fields RNAiPlateID
    # and 96well). Clone is determined the same way as described in
    # update_Clone_table (i.e., clone column for sjj clones, and source
    # plate@well for mv clones). No parent for L4440 wells. Parent for other
    # plates determined using fields 384PlateID, chromosome, and 384Well.
    legacy_query_primary = ('SELECT RNAiPlateID, 96well, clone, '
                            'chromosome, 384PlateID, 384Well '
                            'FROM RNAiPlate')

    def sync_primary_row(legacy_row):
        plate_name = legacy_row[0]
        well = get_three_character_well(legacy_row[1])
        clone_name = legacy_row[2]
        parent_plate_name = legacy_row[4]

        if re.match('sjj', clone_name):
            parent_chromosome = legacy_row[3]
            parent_plate_name = get_ahringer_384_plate_name(parent_chromosome,
                                                            parent_plate_name)
        parent_well_improper = legacy_row[5]
        if re.match('mv', clone_name):
            clone_name = get_vidal_clone_name(parent_plate_name,
                                              parent_well_improper)

        intended_clone = get_clone(clone_name)

        if re.match('L4440', clone_name):
            parent_stock = None

        else:
            parent_well_proper = get_three_character_well(parent_well_improper)
            parent_stock = get_library_stock(parent_plate_name,
                                             parent_well_proper)

            # Confirm that this intended clone matches parent's clone
            if parent_stock.intended_clone != intended_clone:
                raise CommandError('Clone {} does not match parent\n'
                                   .format(clone_name))

        new_well = LibraryStock(
            id=get_library_stock_name(plate_name, well),
            plate=get_library_plate(plate_name), well=well,
            parent_stock=parent_stock,
            intended_clone=intended_clone)

        return update_or_save_object(command, new_well, recorded_wells,
                                     fields_to_compare)

    # L4440 wells from secondary screen are treated specially (since
    # the complicated join used to resolve parents below complicates things
    # for L4440). L4440 wells have no recorded parent.
    legacy_query_secondary_L4440 = ('SELECT RNAiPlateID, 96well '
                                    'FROM CherryPickRNAiPlate '
                                    'WHERE clone = "L4440"')

    def sync_secondary_L4440_row(legacy_row):
        plate_name = legacy_row[0]
        well = get_three_character_well(legacy_row[1])

        new_well = LibraryStock(
            id=get_library_stock_name(plate_name, well),
            plate=get_library_plate(plate_name), well=well,
            parent_stock=None, intended_clone=get_clone('L4440'))

        return update_or_save_object(command, new_well, recorded_wells,
                                     fields_to_compare)

    # Secondary well layout is captured in CherryPickRNAiPlate table (fields
    # RNAiPlate and 96well). However, there are no columns in this table
    # for parent. CherryPickTemplate captures some parent relationships,
    # but not all. Therefore, we rely on CherryPickTemplate where available
    # to define parent relationship. Otherwise, we guess based on clone name
    # (which almost always uniquely defines the source well). In cases not
    # in CherryPickTemplate and where there is ambiguity, leave the parent
    # undefined (we need go back through physical notes to resolve these).
    legacy_query_secondary = (
        'SELECT C.RNAiPlateID as plate, C.96well as well, C.clone, '
        'T.RNAiPlateID as definite_parent_plate, '
        'T.96well as definite_parent_well, '
        'R.RNAiPlateID as likely_parent_plate, '
        'R.96well as likely_parent_well, '
        'R.clone as likely_parent_clone '
        'FROM CherryPickRNAiPlate AS C '
        'LEFT JOIN CherryPickTemplate AS T '
        'ON finalRNAiPlateID = C.RNAiPlateID AND final96well = C.96well '
        'LEFT JOIN RNAiPlate AS R ON C.clone=R.clone AND '
        '(T.RNAiPlateID IS NULL OR '
        '(T.RNAiPlateID=R.RNAiPlateID AND T.96well=R.96well)) '
        'WHERE C.clone != "L4440" '
        'ORDER BY C.RNAiPlateID, C.96well')

    def sync_secondary_row(legacy_row):
        plate_name = legacy_row[0]
        well = get_three_character_well(legacy_row[1])
        clone_name = legacy_row[2]

        definite_parent_plate_name = legacy_row[3]
        definite_parent_well = legacy_row[4]
        if definite_parent_well:
            definite_parent_well = get_three_character_well(
                definite_parent_well)

        likely_parent_plate_name = legacy_row[5]
        likely_parent_well = legacy_row[6]
        if likely_parent_well:
            likely_parent_well = get_three_character_well(likely_parent_well)

        likely_parent_clone_name = legacy_row[7]

        if (definite_parent_plate_name and likely_parent_plate_name and
                definite_parent_plate_name != likely_parent_plate_name):
            raise CommandError(
                'ERROR: definite and likely parent plates disagree '
                'for {} {}\n'.format(plate_name, well))

        if (definite_parent_well and likely_parent_well and
                definite_parent_well != likely_parent_well):
            raise CommandError(
                'ERROR: definite and likely parent wells disagree '
                'for {} {}\n'.format(plate_name, well))

        try:
            if definite_parent_plate_name and definite_parent_well:
                parent_stock = get_library_stock(definite_parent_plate_name,
                                                 definite_parent_well)

            else:
                parent_stock = get_library_stock(likely_parent_plate_name,
                                                 likely_parent_well)

            intended_clone = parent_stock.intended_clone

        except ObjectDoesNotExist:
            command.stderr.write(
                'WARNING for LibraryStock {} {}: parent not '
                'found in LibraryStock\n'.format(plate_name, well))

            parent_stock = None
            intended_clone = None

        if clone_name and (clone_name != likely_parent_clone_name):
            command.stderr.write(
                'WARNING for LibraryStock {} {}: clone recorded '
                'in CherryPickRNAiPlate is inconsistent with '
                'CherryPickTemplate source/destination records\n'
                .format(plate_name, well))

        if re.match('sjj', clone_name):
            try:
                recorded_clone = get_clone(clone_name)
                if recorded_clone != intended_clone:
                    command.stderr.write(
                        'WARNING for LibraryStock {} {}: clone recorded '
                        'in CherryPickRNAiPlate does not match its '
                        'parent\'s clone\n'.format(plate_name, well))

            except ObjectDoesNotExist:
                command.stderr.write(
                    'WARNING for LibraryStock {} {}: clone recorded in '
                    'CherryPickRNAiPlate not found at all in RNAiPlate\n'
                    .format(plate_name, well))

        new_well = LibraryStock(
            id=get_library_stock_name(plate_name, well),
            plate=get_library_plate(plate_name), well=well,
            parent_stock=parent_stock,
            intended_clone=intended_clone)

        return update_or_save_object(command, new_well, recorded_wells,
                                     fields_to_compare)

    legacy_query_eliana = (
        'SELECT RNAiPlateID, 96well, OldPlateID, OldWellPosition '
        'FROM ReArrayRNAiPlate WHERE RNAiPlateID LIKE "Eliana%"')

    def sync_eliana_row(legacy_row):
        plate_name = legacy_row[0]
        well = get_three_character_well(legacy_row[1])

        if legacy_row[2]:
            try:
                parent_stock = get_library_stock(legacy_row[2], legacy_row[3])
                intended_clone = parent_stock.intended_clone
            except ObjectDoesNotExist:
                parent_stock = None
                intended_clone = None

        else:
            parent_stock = None
            intended_clone = None

        new_well = LibraryStock(
            id=get_library_stock_name(plate_name, well),
            plate=get_library_plate(plate_name), well=well,
            parent_stock=parent_stock,
            intended_clone=intended_clone)

        return update_or_save_object(command, new_well, recorded_wells,
                                     fields_to_compare)

    sync_rows(command, cursor, legacy_query_source, sync_source_row)
    sync_rows(command, cursor, legacy_query_primary, sync_primary_row)
    sync_rows(command, cursor, legacy_query_eliana, sync_eliana_row)
    sync_rows(command, cursor, legacy_query_secondary_L4440,
              sync_secondary_L4440_row)
    sync_rows(command, cursor, legacy_query_secondary, sync_secondary_row)
