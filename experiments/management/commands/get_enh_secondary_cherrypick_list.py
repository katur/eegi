from django.core.management.base import NoArgsCommand

from experiments.helpers.scores import (get_secondary_candidates,
                                        passes_enh_secondary_criteria)


HELP = '''
Get the library wells to be cherry-picked for the Enhancer Secondary screen.

This list is based on the manual scores of the Enhancer Primary screen.

'''


class Command(NoArgsCommand):
    help = HELP

    def handle_noargs(self, **options):
        secondary_by_worm, secondary_by_clone = get_secondary_candidates(
            'ENH', passes_enh_secondary_criteria)

        self.stdout.write('Total clones to cherry pick: {}\n'.format(
            len(secondary_by_clone)))

        self.stdout.write('\n\nBreakdown before accounting for universals:\n')
        for worm in sorted(secondary_by_worm):
            self.stdout.write('{}: {} wells\n'.format(
                worm.genotype, len(secondary_by_worm[worm])))

        secondary_by_worm['universal'] = []

        for well in secondary_by_clone:
            worms = (secondary_by_clone[well])
            if len(worms) == 0:
                self.stdout.write('ERROR: length 0')

            # Extract hub candidate clones from unique lists into 'universal'
            # list, to be tested against all mutants
            elif len(worms) >= 4:
                secondary_by_worm['universal'].append(well)
                for worm in worms:
                    secondary_by_worm[worm].remove(well)

        self.stdout.write('\n\nBreakdown after accounting for universals:\n')
        for key in sorted(secondary_by_worm):
            if hasattr(key, 'genotype'):
                label = key.genotype
            else:
                label = key

            self.stdout.write('{}: {} wells\n'.format(
                label, len(secondary_by_worm[key])))
