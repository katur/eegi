from django.core.management.base import BaseCommand

from experiments.helpers.criteria import passes_enh_secondary_criteria
from experiments.helpers.scores import get_secondary_candidates
from library.helpers.plate_design import (assign_to_plates,
                                          get_plate_assignment_rows)
from library.helpers.plate_layout import is_symmetric


HELP = '''
Get the library wells to be cherry-picked for the Enhancer Secondary screen,
and assign to new plates.

This list is based on the manual scores of the Enhancer Primary screen.

'''

UNIVERSAL_THRESHOLD = 4


class Command(BaseCommand):
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('--summary',
                            dest='summary',
                            action='store_true',
                            default=False,
                            help='Print summary of counts only')

    def print_candidates_by_worm(self, candidates_by_worm):
        total = 0
        for worm in sorted(candidates_by_worm):
            label = worm.genotype if hasattr(worm, 'genotype') else worm
            num_candidates = len(candidates_by_worm[worm])
            total += num_candidates
            self.stdout.write('\t{}: {} wells'.format(label, num_candidates))

        self.stdout.write('Total: {} wells'.format(total))

    def handle(self, **options):
        summary_mode = options['summary']

        # Get all enhancery secondary candidates, organized by worm and clone
        candidates_by_worm, candidates_by_clone = get_secondary_candidates(
            'ENH', passes_enh_secondary_criteria)

        if summary_mode:
            self.stdout.write('Total clones to cherry pick: {}'
                              .format(len(candidates_by_clone)))
            self.stdout.write('\n\nBefore accounting for universals:')
            self.print_candidates_by_worm(candidates_by_worm)

        # Move relevant clones from individual worm lists to 'universal' list
        candidates_by_worm['universal'] = []
        for well in candidates_by_clone:
            worms = (candidates_by_clone[well])
            if len(worms) >= UNIVERSAL_THRESHOLD:
                candidates_by_worm['universal'].append(well)
                for worm in worms:
                    candidates_by_worm[worm].remove(well)

        if summary_mode:
            self.stdout.write('\n\nAfter accounting for universals:')
            self.print_candidates_by_worm(candidates_by_worm)

        # Create official cherry pick list, including randomized empty wells
        cherrypick_list = []
        for worm, candidates in candidates_by_worm.iteritems():
            label = worm.allele if hasattr(worm, 'allele') else worm

            if label == 'universal':
                num_empties = 1
            elif label == 'it57':
                num_empties = 0
            else:
                num_empties = 2

            assigned = assign_to_plates(sorted(candidates),
                                        num_empties=num_empties)

            rows = get_plate_assignment_rows(assigned)

            for row in rows:
                if row[2]:
                    source_plate = row[2].plate
                    source_well = row[2].well
                else:  # Empty well
                    source_plate = None
                    source_well = None

                destination_plate = label + '_E' + str(row[0] + 1)
                destination_well = row[1]
                cherrypick_list.append((source_plate, source_well,
                                        destination_plate,
                                        destination_well))

        # Sort by (destination_plate, destination_well)
        cherrypick_list.sort(
            key=lambda x: (x[2].split('_')[0], int(x[2].split('E')[1]),
                           int(x[3][1:]), x[3][0]))

        # Double check and print empty wells in summary mode
        if summary_mode:
            self.stdout.write('\n\nEmpty wells:\n')
            e = {}
            for row in cherrypick_list:
                if row[0] is None:
                    if row[2] not in e:
                        e[row[2]] = set()
                    e[row[2]].add(row[3])

            seen = set()
            for plate, wells in e.iteritems():
                wells = tuple(sorted(wells))
                self.stdout.write('\t{}: {}'.format(plate, wells))
                if wells in seen:
                    self.stdout.write('ERROR: already seen!')
                seen.add(wells)

                if is_symmetric(wells):
                    self.stdout.write('ERROR: symmetric!')
            return

        # Print the list
        self.stdout.write('source_plate, source_well, '
                          'destination_plate, destination_well')
        for row in cherrypick_list:
            self.stdout.write(','.join([str(x) for x in row]))
