import sys

from django.core.management.base import BaseCommand

from worms.models import WormStrain
from library.models import LibraryWell

from utils.helpers.scores import get_condensed_primary_scores


class Command(BaseCommand):
    help = ('Get ENH cherry picking list')

    def handle(self, *args, **options):
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

        sys.stdout.write('Before accounting for universals: \n')
        for worm in secondary_by_worm:
            sys.stdout.write('{}: {} wells\n'.format(
                worm, len(secondary_by_worm[worm])))
        sys.stdout.write('\n\n\n')

        sys.stdout.write('Total clones to cherry pick: '.format(
            len(secondary_by_clone)))

        num_universal = 0
        num_unique = 0
        for well in secondary_by_clone:
            num = len(secondary_by_clone[well])
            if num == 0:
                sys.stdout.write('ERROR: length 0')
            elif num >= 3:
                num_universal += 1
            else:
                num_unique += 1

        sys.stdout.write('Breakdown: {} universal, {} unique'.format(
            num_universal, num_unique))
