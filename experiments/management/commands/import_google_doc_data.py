from django.core.management.base import BaseCommand, CommandError

from experiments.helpers.create import parse_batch_data_entry_gdoc
from utils.scripting import require_db_write_acknowledgement


class Command(BaseCommand):
    help = 'Import batch experiments recorded in Google Doc'

    def handle(self, **options):
        try:
            count = parse_batch_data_entry_gdoc(dry_run=True)
        except Exception as e:
            raise CommandError(e)

        self.stdout.write('Dry run complete. '
                          '{} experiment plates found in sheet.'
                          .format(count))

        require_db_write_acknowledgement('Proceed to actual run? '
                                         '(yes/no) ')

        try:
            count = parse_batch_data_entry_gdoc()
        except Exception as e:
            raise CommandError(e)

        self.stdout.write('Actual run complete. '
                          '{} experiment plates added to database.'
                          .format(count))
