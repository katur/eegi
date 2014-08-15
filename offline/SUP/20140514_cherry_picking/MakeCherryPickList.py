import csv
import math
from Clone import Clone
from Mutant import get_mutant
from ScoreData import ExperimentScoreData, CloneScoreData
from Plate import (get_destination_wells,
                   get_destination_plates_and_start,
                   plates)
from WellToTile import get_tile


def get_other_clones(clone):
    mapping = clone_to_mapping[clone]
    if mapping == 'NULL' or mapping == '':
        return [clone]
    else:
        mapped_clones = mapping_to_clones[mapping]
        if len(mapped_clones) > 10:
            raise RuntimeWarning(mapping + ' has over 10 mapped clones')
        return mapped_clones


###############################################################################
print 'Adding clones to all_scores and creating helper dictionaries...\n'
###############################################################################
primary_plates = set()
with open('input/PrimaryPlates.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        primary_plates.add(row[0])

# all_scores = {clone: {mutant: {expID: score_data}}}
all_scores = {}
clone_to_mapping = {}
mapping_to_clones = {}
with open('input/PrimaryClones.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        clone = Clone(row[0], row[2], row[3])
        mapping = row[1]

        # Add all clones to all_scores and clone_to_mapping
        assert clone not in clone_to_mapping and clone not in all_scores
        all_scores[clone] = {}
        clone_to_mapping[clone] = mapping

        # Add to mapping_to_clone
        if mapping not in mapping_to_clones:
            mapping_to_clones[mapping] = []
        mapping_to_clones[mapping].append(clone)


###############################################################################
print 'Adding scores to all_scores...\n'
###############################################################################
with open('input/AllNonJunkSupPrimaryScores.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        clone = Clone(row[0], row[1], row[2])
        gene = row[3]
        temperature = row[4]
        expID = int(row[5])
        expDate = row[8]
        score = int(row[6])
        scorer = row[7]

        mutant = get_mutant(gene)
        if mutant.temperature != temperature:
            continue

        assert clone in all_scores
        scored_mutants = all_scores[clone]
        if mutant not in scored_mutants:
            scored_mutants[mutant] = {}

        experiments = scored_mutants[mutant]
        if expID not in experiments:
            experiments[expID] = ExperimentScoreData()

        score_data = experiments[expID]
        score_data.add_score(score)
        score_data.add_scorer(scorer)
        score_data.add_date(expDate)


###############################################################################
print 'Adding scored positives to secondary_clones...\n'
###############################################################################
secondary_clones = {}
missing_scored_by_noah = 0
missing_scored_not_by_noah = 0
for clone in all_scores:
    scored_mutants = all_scores[clone]
    for mutant in scored_mutants:
        experiments = scored_mutants[mutant]
        net_score_data = CloneScoreData()

        for expID in experiments:
            score_data = experiments[expID]
            net_score_data.add_experiment_score_data(score_data)

        # If positive, add it to secondary_clones
        # (along with all clones with the same gene mapping)
        if net_score_data.is_accepted(mutant):
            other_clones = get_other_clones(clone)
            for clone in other_clones:
                if clone not in secondary_clones:
                    secondary_clones[clone] = set()
                secondary_clones[clone].add(mutant)


###############################################################################
print 'Add any additional clones that were already included...\n'
###############################################################################
tested_secondary_clones = {}
with open('input/ActualSecondaryClones.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        clone = Clone(row[0], row[1], row[2])
        gene = row[3]
        mutant = get_mutant(gene)

        if clone not in tested_secondary_clones:
            tested_secondary_clones[clone] = []

        tested_mutants = tested_secondary_clones[clone]
        if mutant not in tested_mutants:
            tested_mutants.append(mutant)

with open('input/ActualSecondaryClones_NoGrow.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        clone = Clone(row[0], row[1], row[2])
        gene = row[3]
        mutant = get_mutant(gene)

        if clone not in tested_secondary_clones:
            tested_secondary_clones[clone] = []

        tested_mutants = tested_secondary_clones[clone]
        if mutant not in tested_mutants:
            tested_mutants.append(mutant)

for clone in tested_secondary_clones:
    tested_mutants = tested_secondary_clones[clone]
    tested_clones = get_other_clones(clone)
    for mutant in tested_mutants:
        for clone in tested_clones:
            if clone not in secondary_clones:
                secondary_clones[clone] = set()
            secondary_clones[clone].add(mutant)


###############################################################################
print 'Finding which secondary clones must be cherry picked...\n'
###############################################################################
missing_clones = {}
missing_by_mutant = {}
plates_to_stamp = set()

do_not_grow_clones = [
    Clone('mv_W05E10.4', '17', 'C11'),
    Clone('sjj_T19B4.6', 'I-2-B1', 'E11'),
    Clone('sjj_F39B2.9', 'I-7-A2', 'D12'),
    Clone('sjj_C37G2.6', 'III-6-B2', 'E02'),
    Clone('sjj_C38C3.4', 'V-1-B1', 'H05'),
    Clone('sjj_Y39B6B.y', 'V-12-A2', 'G04'),
    Clone('sjj_Y5H2B.f', 'V-2-A1', 'D12'),
    Clone('sjj_F08F3.4', 'V-4-A1', 'H12'),
    Clone('sjj_ZC317.5', 'V-4-A2', 'A10'),
    Clone('sjj_F26F12.7', 'V-4-A2', 'H08'),
    Clone('sjj_F13H6.1', 'V-4-B1', 'G09'),
    Clone('sjj_F20A1.5', 'V-5-A1', 'D08'),
    Clone('sjj_ZK994.3', 'V-6-A1', 'C12'),

]

for clone, mutants in secondary_clones.iteritems():
    if clone in do_not_grow_clones:
        continue

    if clone in tested_secondary_clones:
        mutants_tested = tested_secondary_clones[clone]
    else:
        mutants_tested = []

    if len(mutants) >= 3:
        if ('universal' not in mutants_tested):
            plates_to_stamp.add(clone.plate)
            if clone not in missing_clones:
                missing_clones[clone] = []
            missing_clones[clone].append('universal')
            if 'universal' not in missing_by_mutant:
                missing_by_mutant['universal'] = []
            missing_by_mutant['universal'].append(clone)

    # need not in be in universal plate
    else:
        for mutant in mutants:
            if ('universal' not in mutants_tested) and (
                    mutant not in mutants_tested):
                plates_to_stamp.add(clone.plate)
                if clone not in missing_clones:
                    missing_clones[clone] = []
                missing_clones[clone].append(mutant)
                if mutant not in missing_by_mutant:
                    missing_by_mutant[mutant] = []
                missing_by_mutant[mutant].append(clone)

# Check that all clones already in three unique plates are in new universal
with open('input/AlreadyShouldBeUniversalClones.csv', 'rb') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        clone_name = row[0]
        found = False
        for clone in missing_by_mutant['universal']:
            if clone.name != clone_name:
                found = True
        assert found is True


###############################################################################
print "======================================================================="
###############################################################################
print '\n{0} total clones in primary (mapping to {1} genes)\n'.format(
    str(len(clone_to_mapping)), str(len(mapping_to_clones)))

'''
for k, v in all_scores.iteritems():
    print 'example of item in all_scores:'
    print k, v
    print '\n'
    break

for k, v in secondary_clones.iteritems():
    print 'example of item in secondary_clones:'
    print k, v
    print '\n'
    break

i = 0
print '\nexamples of missing clones:'
for k, v in missing_clones.iteritems():
    print k, v
    i += 1
    if i >= 10:
        break
'''
print 'number of clones missing from secondary: {0}'.format(
    str(len(missing_clones)))


def get_number_of_columns(x):
    return int(math.ceil(x / 8.0))


def get_remainder(x):
    return x % 8


mutlist = []
for k, v in missing_by_mutant.iteritems():
    wells = len(v)
    columns = get_number_of_columns(wells)
    remainder = get_remainder(wells)
    mutlist.append((wells, columns, k, remainder))

for item in sorted(mutlist, reverse=True):
    print '{2}: {0} clones, {1} columns, {3} remainder'.format(
        item[0], item[1], item[2], item[3])

print '\nnumber of plates to stamp: {0}'.format(str(len(plates_to_stamp)))
no_need_to_stamp_plates = primary_plates - plates_to_stamp

'''
print 'plates to not stamp:'
for plate in sorted(no_need_to_stamp_plates):
    print plate
'''

with open('output/clone_stamp_list.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for k, v in sorted(missing_clones.iteritems()):
        writer.writerow([k.plate, k.well, k.name, str(v)])


with open('output/cherry_picking_list.csv', 'wb') as cp_file, open(
        'output/database_list.csv', 'wb') as db_file:
    cp_writer = csv.writer(cp_file, delimiter=',')
    db_writer = csv.writer(db_file, delimiter=',')

    cp_writer.writerow(['clone', 'source plate', 'source well', 'mutant',
                        'destination plate', 'destination well'])
    db_writer.writerow(['mutant', 'mutantAllele', 'RNAiPlateID', '96well',
                        'ImgName', 'clone', 'node_primary_name',
                        'seq_node_primary_name'])

    for mutant, clones in sorted(missing_by_mutant.iteritems()):
        destination_plates, starting_well = get_destination_plates_and_start(
            mutant)
        destination_plate_index = 0
        destination_wells = get_destination_wells(mutant)
        destination_well_index = destination_wells.index(starting_well)

        for clone in sorted(clones):
            destination_plate = destination_plates[destination_plate_index]
            destination_well = destination_wells[destination_well_index]
            destination_tile = get_tile(destination_well)

            cp_writer.writerow([
                clone.name, clone.plate, clone.well, mutant,
                destination_plate, destination_well
            ])

            # CherryPickRNAiPlate table in GenomeWideGI database expects:
            # mutant, mutantAllele, RNAiPlateID, 96well, ImgName, clone,
            # node_primary_name, seq_node_primary_name
            db_writer.writerow([
                destination_plate.db_mutant, destination_plate.db_mutantAllele,
                destination_plate.db_RNAiPlateID, destination_well,
                destination_tile, clone.name, clone_to_mapping[clone], 'X'
            ])
            destination_well_index += 1
            if destination_well_index == len(destination_wells):
                destination_plate_index += 1
                destination_well_index = 0

    for k in plates:
        destination_plate = plates[k]
        for column in ['02', '07', '11']:
            if destination_plate.deep_well == "universal" and column == '07':
                continue
            for row in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
                destination_well = row + column
                destination_tile = get_tile(destination_well)
                db_writer.writerow([
                    destination_plate.db_mutant,
                    destination_plate.db_mutantAllele,
                    destination_plate.db_RNAiPlateID,
                    destination_well, destination_tile,
                    'L4440', 'L4440', 'X'
                ])
