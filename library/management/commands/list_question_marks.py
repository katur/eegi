import argparse
import sys

from django.core.management.base import BaseCommand

from clones.models import Clone
from library.models import LibraryStock


class Command(BaseCommand):
    help = 'Parse ambiguities from output of LibrarStock legacy sync'

    def add_arguments(self, parser):
        parser.add_argument(
            'input_file', type=argparse.FileType('r'),
            help="trace of database syncing step for stocks")

    def handle(self, **options):
        for row in options['input_file']:
            if not row.startswith('WARNING:'):
                continue

            words = row.split()
            stock = LibraryStock.objects.get(id=words[2])
            parent1 = LibraryStock.objects.get(id=words[10][:-1])
            parent2 = LibraryStock.objects.get(id=words[12][:-2])
            clone1 = Clone.objects.get(id=words[17][:-1])
            clone2 = Clone.objects.get(id=words[19][:-2])
            sys.stdout.write('{} either {}:{} or {}:{}\n'.format(
                stock, parent1, clone1, parent2, clone2))
