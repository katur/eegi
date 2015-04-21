from django.core.management.base import NoArgsCommand

from experiments.helpers.criteria import passes_enh_secondary_criteria
from experiments.helpers.scores import get_secondary_candidates
from library.helpers.plate_design import (assign_to_plates,
                                          get_plate_assignment_rows)


HELP = '''
Get the library wells to be cherry-picked for the Enhancer Secondary screen.

This list is based on the manual scores of the Enhancer Primary screen.

'''


class Command(NoArgsCommand):
    help = HELP

    def handle_noargs(self, **options):
        candidates_by_worm, candidates_by_clone = get_secondary_candidates(
            'ENH', passes_enh_secondary_criteria)

        # Print information about the number of clones per worm
        self.stdout.write('Total clones to cherry pick: {}\n'.format(
            len(candidates_by_clone)))

        self.stdout.write('\n\nBreakdown before accounting for universals:\n')
        for worm in sorted(candidates_by_worm):
            self.stdout.write('{}: {} wells\n'.format(
                worm.genotype, len(candidates_by_worm[worm])))

        # Move relevant clones into 'universal' list, to be tested against
        # all mutants
        candidates_by_worm['universal'] = []

        for well in candidates_by_clone:
            worms = (candidates_by_clone[well])
            if len(worms) == 0:
                self.stdout.write('ERROR: length 0')

            elif len(worms) >= 4:
                candidates_by_worm['universal'].append(well)
                for worm in worms:
                    candidates_by_worm[worm].remove(well)

        # Print information about the number of clones per worm, now that
        # some have been consolidated to the universal plate
        cherrypick_list = []
        self.stdout.write('\n\nBreakdown after accounting for universals:\n')
        for k in sorted(candidates_by_worm):
            if hasattr(k, 'get_short_genotype'):
                label = k.get_short_genotype()
            else:
                label = k

            self.stdout.write('{}: {} wells\n'.format(
                label, len(candidates_by_worm[k])))

            assigned = assign_to_plates(sorted(candidates_by_worm[k]))
            rows = get_plate_assignment_rows(assigned)

            for row in rows:
                cherrypick_list.append((row[2].plate,
                                        row[2].well,
                                        label + '_E' + str(row[0]),
                                        row[1]))

        # Print cherry-picking list
        cherrypick_list.sort()
        self.stdout.write('\n\nsource_plate, source_well, '
                          'destination_plate, destination_well\n')
        for row in cherrypick_list:
            self.stdout.write(','.join([str(x) for x in row]) + '\n')

        # TODO: add new library plates to database
