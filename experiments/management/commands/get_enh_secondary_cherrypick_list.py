from django.core.management.base import BaseCommand

from experiments.helpers.criteria import passes_enh_secondary_criteria
from experiments.helpers.scores import get_secondary_candidates
from library.helpers.plate_design import (assign_to_plates,
                                          get_plate_assignment_rows)


HELP = '''
Get the library wells to be cherry-picked for the Enhancer Secondary screen.

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

        parser.add_argument('--tech_format',
                            dest='tech_format',
                            action='store_true',
                            default=False,
                            help=('Print the list with spacing more amenable '
                                  'to the physical cherry-picking process'))

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
        tech_mode = options['tech_format']

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

        # Create cherry pick list, including empty wells
        cherrypick_list = []
        for worm, candidates in candidates_by_worm.iteritems():
            label = worm.allele if hasattr(worm, 'allele') else worm
            if label == 'universal':
                num_empties = 1
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

        # Keep track of source/destination plate combos in order
        # to partition results by this (helps techs to cherry pick)
        num_combos = 0
        previous_combo = (cherrypick_list[0][0], cherrypick_list[0][2])

        # Printing and analysis
        if not summary_mode:
            self.stdout.write('source_plate, source_well, '
                              'destination_plate, destination_well')

        destination_plates = set()
        empties = []

        for row in cherrypick_list:
            source_plate = row[0]
            destination_plate = row[2]

            destination_plates.add(destination_plate)
            if source_plate is None:
                empties.append(row)

            current_combo = (source_plate, destination_plate)
            if current_combo != previous_combo:
                num_combos += 1
                previous_combo = current_combo
                if tech_mode:
                    self.stdout.write('\n')

            if not summary_mode:
                self.stdout.write(','.join([str(x) for x in row]))

        if tech_mode or summary_mode:
            self.stdout.write('\n\n{} destination plates.'
                              '\n\n{} origin/destination combos.'
                              .format(len(destination_plates),
                                      num_combos))
