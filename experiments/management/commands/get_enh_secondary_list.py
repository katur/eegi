from django.core.management.base import NoArgsCommand

from experiments.helpers import get_condensed_primary_scores
from library.models import LibraryWell
from worms.models import WormStrain


HELP = '''
Get the list of clones to be cherry picked for the ENH secondary.

This list is based on the manual scores of the ENH primary.
'''


class Command(NoArgsCommand):
    help = HELP

    def handle_noargs(self, **options):
        enhancer_worms = WormStrain.objects.exclude(
            permissive_temperature__isnull=True)
        wells = LibraryWell.objects.filter(plate__screen_stage=1)

        secondary_by_worm = {}
        secondary_by_clone = {}

        for worm in enhancer_worms:
            secondary_by_worm[worm] = []
            for well in wells:
                scores = get_condensed_primary_scores(worm, well, 'ENH')
                if 4 in scores or 3 in scores or scores == [2, 2]:
                    secondary_by_worm[worm].append(well)
                    if well not in secondary_by_clone:
                        secondary_by_clone[well] = []
                    secondary_by_clone[well].append(worm)

        self.stdout.write('Total clones to cherry pick: {}\n'.format(
            len(secondary_by_clone)))

        self.stdout.write('\n\nBreakdown before accounting for universals:\n')
        for worm in secondary_by_worm:
            self.stdout.write('{}: {} wells\n'.format(
                worm, len(secondary_by_worm[worm])))

        secondary_by_worm['universal'] = []

        for well in secondary_by_clone:
            worms = (secondary_by_clone[well])
            if len(worms) == 0:
                self.stdout.write('ERROR: length 0')

            # Extract hub candidate clones from unique lists into 'univeral'
            # list, to be tested against all mutants
            elif len(worms) >= 13:
                secondary_by_worm['universal'].append(well)
                for worm in worms:
                    secondary_by_worm[worm].remove(well)

        self.stdout.write('\n\nBreakdown after accounting for universals:\n')
        for worm in secondary_by_worm:
            self.stdout.write('{}: {} wells\n'.format(
                worm, len(secondary_by_worm[worm])))

        for well in secondary_by_worm['universal']:
            print well
