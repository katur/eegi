from django.core.management.base import BaseCommand

from experiments.helpers.criteria import passes_enh_primary
from utils.plates import (assign_to_plates, get_plate_assignment_rows,
                          is_symmetric)
from worms.helpers.queries import get_worms_for_screen_type

UNIVERSAL_THRESHOLD = 4


class Command(BaseCommand):
    """
    Command to generate the ENH secondary cherrypick list.

    Determines the library wells to be cherrypicked for the ENH
    secondary screen, and assigns them to new plates.

    This list is based on the manual scores of the ENH Primary screen.
    """

    help = 'Generate the ENH secondary cherrypick list.'

    def add_arguments(self, parser):
        parser.add_argument('--summary',
                            dest='summary',
                            action='store_true',
                            default=False,
                            help='Print summary of counts only')

    def handle(self, **options):
        summary_mode = options['summary']

        candidates_by_worm = {}
        candidates_by_clone = {}
        worms = get_worms_for_screen_type('ENH')

        for worm in worms:
            candidates_by_worm[worm] = []
            singles = worm.get_stocks_tested_by_number_of_replicates(
                'ENH', 1, 1)

            positives = worm.get_positives(
                'ENH', 1, passes_enh_primary, singles=singles)

            for library_stock in positives:
                candidates_by_worm[worm].append(library_stock)
                if library_stock not in candidates_by_clone:
                    candidates_by_clone[library_stock] = []
                candidates_by_clone[library_stock].append(worm)

        if summary_mode:
            self.stdout.write('Total clones to cherrypick: {}'
                              .format(len(candidates_by_clone)))

            self.stdout.write('\n\nBefore accounting for universals:')
            _print_candidates_by_worm(candidates_by_worm)

        # Move certain clones from individual worm lists to universal
        candidates_by_worm['universal'] = []
        for well in candidates_by_clone:
            worms = (candidates_by_clone[well])
            if len(worms) >= UNIVERSAL_THRESHOLD:
                candidates_by_worm['universal'].append(well)
                for worm in worms:
                    candidates_by_worm[worm].remove(well)

        if summary_mode:
            self.stdout.write('\n\nAfter accounting for universals:')
            _print_candidates_by_worm(candidates_by_worm)
            return

        # Create official cherrypick list, with random empty wells
        cherrypick_list = []
        already_used_empties = set()
        for worm, candidates in candidates_by_worm.iteritems():
            label = worm.allele if hasattr(worm, 'allele') else worm

            if label == 'universal':
                empties_per_plate = 1
                empties_limit = 9
            elif label == 'it57':
                empties_per_plate = 0
                empties_limit = None
            else:
                empties_per_plate = 2
                empties_limit = None

            assigned = assign_to_plates(
                sorted(candidates),
                vertical=True,
                empties_per_plate=empties_per_plate,
                empties_limit=empties_limit,
                already_used_empties=already_used_empties)

            rows = get_plate_assignment_rows(assigned)

            for row in rows:
                if row[2]:
                    source_plate = row[2].plate
                    source_well = row[2].well
                else:  # Empty well
                    source_plate = None
                    source_well = None

                destination_plate = label + '-E' + str(row[0] + 1)
                destination_well = row[1]
                cherrypick_list.append((source_plate, source_well,
                                        destination_plate,
                                        destination_well))

        # Sort by (destination_plate, destination_well)
        cherrypick_list.sort(
            key=lambda x: (x[2].split('-')[0], int(x[2].split('E')[1]),
                           int(x[3][1:]), x[3][0]))

        # Print the list
        self.stdout.write('source_plate,source_well,'
                          'destination_plate,destination_well')
        for row in cherrypick_list:
            self.stdout.write(','.join([str(x) for x in row]))

        # Quick fix for empty_wells check up to this point not accounting
        # for not-full plates potentially having the same plate pattern,
        # despite the "chosen" empty wells differing.
        # If the printed list says "TRASH THIS" at the bottom, try again!
        e = {}
        for row in cherrypick_list:
            if row[0] is None:
                if row[2] not in e:
                    e[row[2]] = set()
                e[row[2]].add(row[3])

        seen = set()
        for plate, wells in e.iteritems():
            wells = tuple(sorted(wells))
            if is_symmetric(wells):
                self.stdout.write('TRASH THIS AND TRY AGAIN. '
                                  '{}:{} pattern is symmetric!'
                                  .format(plate, wells))

            if wells in seen:
                self.stdout.write('TRASH THIS AND TRY AGAIN. '
                                  '{}:{} pattern redundant!'
                                  .format(plate, wells))

            seen.add(wells)


def _print_candidates_by_worm(command, candidates_by_worm):
    total = 0
    for worm in sorted(candidates_by_worm):
        label = worm.genotype if hasattr(worm, 'genotype') else worm
        num_candidates = len(candidates_by_worm[worm])
        total += num_candidates
        command.stdout.write('\t{}: {} wells'.format(label, num_candidates))

    command.stdout.write('Total: {} wells'.format(total))
