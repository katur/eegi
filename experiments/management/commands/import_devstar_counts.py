from itertools import chain
import os

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.management.base import BaseCommand, CommandError

from experiments.models import Experiment, DevstarScore
from utils.scripting import require_db_write_acknowledgement


PATTERNS = ('bacteria', 'W', 'LC', 'EC', 'NewcntW', 'NewcntL')


class Command(BaseCommand):
    help = ('WORK IN PROGRESS -- does not yet save anything to database. '
            'Waiting on Lior to normalize cnt.txt output. '
            'Parse DevStaR txt output, to add to this database.')

    def add_arguments(self, parser):
        parser.add_argument('--all', action='store_true', dest='all',
                            default=False,
                            help=('Parse all experiments, instead of just '
                                  'those without DevStaR counts in the '
                                  'database'))

    def handle(self, **options):
        require_db_write_acknowledgement()
        return

        if options['all']:
            experiments = Experiment.objects.all()
        else:
            null_devstar_experiment_pks = (
                DevstarScore.objects.filter(
                    area_adult__isnull=True,
                    area_larva__isnull=True,
                    area_embryo__isnull=True)
                .values_list('experiment', flat=True))

            null_devstar_experiments = Experiment.objects.filter(
                pk__in=null_devstar_experiment_pks)

            all_devstar_experiment_pks = (
                DevstarScore.objects.all()
                .values_list('experiment', flat=True))

            no_devstar_experiments = Experiment.objects.exclude(
                pk__in=all_devstar_experiment_pks)

            experiments = sorted(
                chain(null_devstar_experiments, no_devstar_experiments),
                key=lambda instance: instance.id)

        for experiment in experiments:
            path = experiment.get_devstar_count_path()

            if not os.path.isfile(path):
                self.stderr.write('WARNING: Skipping experiment {} due to '
                                  'DevStaR file not found'
                                  .format(experiment))
                continue

            counts = [None] * 6

            with open(path, 'r') as f:
                for line in f:
                    for i, pattern in enumerate(PATTERNS):
                        if line.startswith(pattern):
                            try:
                                counts[i] = int(line.split()[1])
                            except Exception:
                                raise CommandError('Error parsing line {} '
                                                   'in experiment {}'
                                                   .format(i, experiment))

            for i, count in enumerate(counts):
                if count is None:
                    self.stderr.write('WARNING: {} count is missing '
                                      'for experiment {}'
                                      .format(PATTERNS[i], experiment))

            new_score = DevstarScore(
                experiment=experiment,
                is_bacteria_present=counts[0], area_adult=counts[1],
                area_larva=counts[2], area_embryo=counts[3],
                count_adult=counts[4], count_larva=counts[5],
            )

            # If score already exists in database, check for match
            try:
                previous_score = DevstarScore.objects.get(
                    experiment=experiment)

                if not previous_score.matches_raw_fields(new_score):
                    raise CommandError('The DevStaR txt output does '
                                       'not match the existing database '
                                       'entry for Experiment {}'
                                       .format(experiment))

            except ObjectDoesNotExist:
                self.stderr.write('DevStaR object not found for {}. '
                                  'Attempting to save.'
                                  .format(experiment))
                try:
                    new_score.full_clean()

                except ValidationError:
                    raise CommandError('Cleaning DevStaR object {} '
                                       'raised ValidationError'
                                       .format(new_score))
                # new_score.save()
