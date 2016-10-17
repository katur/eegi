import argparse

from django.core.management.base import BaseCommand

from library.models import LibraryStock


class Command(BaseCommand):
    help = 'Parse ambiguities from output of LibrarStock legacy sync'

    def add_arguments(self, parser):

        parser.add_argument(
            'cherrypick_list', type=argparse.FileType('r'),
            help='ENH secondary cherrypick list')

    def handle(self, **options):
        for row in options['cherrypick_list']:
            items = row.split(',')
            dest_plate, dest_well, source_plate, source_well = items[:4]
            if source_plate == 'None':
                continue

            dest = dest_plate.replace('_', '-') + '_' + dest_well
            dest = LibraryStock.objects.get(id=dest)

            try:
                int(source_plate)
                source_plate = 'vidal-' + source_plate
            except ValueError:
                pass

            source = source_plate + '_' + source_well
            source = LibraryStock.objects.get(id=source)

            if (dest.parent_stock != source or
                    dest.intended_clone != source.intended_clone):
                print 'changing {} to {}, {}'.format(
                    dest, source, source.intended_clone)
                dest.parent_stock = source
                dest.intended_clone = source.intended_clone
                dest.save()
