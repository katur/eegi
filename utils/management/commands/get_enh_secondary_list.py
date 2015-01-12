import sys

from django.core.management.base import BaseCommand

from worms.models import WormStrain
from library.models import LibraryWell

from utils.helpers.primary_to_secondary import get_condensed_primary_scores


class Command(BaseCommand):
    help = ('Get ENH cherry picking list')

    def handle(self, *args, **options):
        enhancer_worms = WormStrain.objects.exclude(
            permissive_temperature__isnull=True)
        wells = LibraryWell.objects.filter(plate__screen_stage=1)

        all_secondary_wells = []
        for worm in enhancer_worms:
            worm_secondary_wells = []
            for well in wells:
                scores = get_condensed_primary_scores(worm, well, 'ENH')
                if 4 in scores or 3 in scores or scores == [2, 2]:
                    output = '{} {} {}\n'.format(scores, worm, well)
                    worm_secondary_wells.append(output)

            sys.stdout.write('{}: {} wells\n'.format(
                worm, len(worm_secondary_wells)))
            all_secondary_wells.extend(worm_secondary_wells)

        sys.stdout.write('\n\nAll strains: {} wells\n'.format(
            len(all_secondary_wells)))
