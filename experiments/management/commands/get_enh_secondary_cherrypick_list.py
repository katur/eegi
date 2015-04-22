from django.core.management.base import BaseCommand

from experiments.helpers.criteria import passes_enh_secondary_criteria
from experiments.helpers.scores import get_secondary_candidates
from library.helpers.plate_design import (assign_to_plates,
                                          get_plate_assignment_rows)


HELP = '''
Get the library wells to be cherry-picked for the Enhancer Secondary screen.

This list is based on the manual scores of the Enhancer Primary screen.

'''


class Command(BaseCommand):
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('--summary',
                            dest='summary',
                            action='store_true',
                            default=False,
                            help='Print summary of counts only')

    def handle(self, **options):
        if options['summary']:
            summary_mode = True
        else:
            summary_mode = False

        # Get all enhancery secondary candidates, organized both by worm
        # and by clone
        candidates_by_worm, candidates_by_clone = get_secondary_candidates(
            'ENH', passes_enh_secondary_criteria)

        if summary_mode:
            self.stdout.write('Total clones to cherry pick: {}'.format(
                len(candidates_by_clone)))

            self.stdout.write('\n\nBreakdown before accounting '
                              'for universals:')
            total = 0
            for worm in sorted(candidates_by_worm):
                num_candidates = len(candidates_by_worm[worm])
                total += num_candidates
                self.stdout.write('\t{}: {} wells'.format(
                    worm.genotype, num_candidates))
            self.stdout.write('Total: {} wells'.format(total))

        # Move relevant clones from individual worm lists to 'universal' list
        candidates_by_worm['universal'] = []
        for well in candidates_by_clone:
            worms = (candidates_by_clone[well])
            if len(worms) >= 4:
                candidates_by_worm['universal'].append(well)
                for worm in worms:
                    candidates_by_worm[worm].remove(well)

        if summary_mode:
            self.stdout.write('\n\nBreakdown after accounting '
                              'for universals:')
            total = 0
            for worm in sorted(candidates_by_worm):
                if hasattr(worm, 'genotype'):
                    label = worm.genotype
                else:
                    label = worm

                num_candidates = len(candidates_by_worm[worm])
                total += num_candidates
                self.stdout.write('\t{}: {} wells'.format(
                    label, num_candidates))
            self.stdout.write('Total: {} wells'.format(total))

        else:
            cherrypick_list = []

            for worm, candidates in candidates_by_worm.iteritems():
                if hasattr(worm, 'allele'):
                    label = worm.allele
                else:
                    label = worm

                assigned = assign_to_plates(sorted(candidates))
                rows = get_plate_assignment_rows(assigned)

                for row in rows:
                    cherrypick_list.append((row[2].plate,
                                            row[2].well,
                                            label + '_E' + str(row[0]),
                                            row[1]))

            cherrypick_list.sort()

            self.stdout.write('source_plate, source_well, '
                              'destination_plate, destination_well')

            for row in cherrypick_list:
                self.stdout.write(','.join([str(x) for x in row]))
