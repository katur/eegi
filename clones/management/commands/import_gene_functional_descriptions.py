import argparse
import csv

from django.core.management.base import BaseCommand, CommandError

from clones.models import Gene
from utils.scripting import require_db_write_acknowledgement

HELP = 'Import gene functional descriptions from Wormbase.'


class Command(BaseCommand):
    help = HELP

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'))

    def handle(self, *args, **options):
        f = options['file']
        require_db_write_acknowledgement()

        descriptions = self.parse_wormbase_file(f)

        genes = Gene.objects.all()

        for gene in genes:
            if gene.id not in descriptions:
                raise CommandError('{} not found in WormBase file'
                                   .format(gene))
            info = descriptions[gene.id]

            # Sanity checks
            molecular_name = info['molecular_name']
            public_name = info['public_name']

            if (not molecular_name.startswith(gene.cosmid_id) and
                    gene.cosmid_id != public_name):
                self.stdout.write('Cosmid mismatch for {}: '
                                  'Firoz says {}, WormBase says {}'
                                  .format(gene, gene.cosmid_id,
                                          molecular_name))

            if (public_name != gene.locus and
                    not molecular_name.startswith(public_name) and
                    not public_name.startswith(gene.cosmid_id)):
                self.stdout.write('Locus mismatch for {}: '
                                  'Firoz says {}, WormBase says {}'
                                  .format(gene, gene.locus, public_name))

            description = info['concise_description']
            gene.functional_description = description
            gene.save()

    def parse_wormbase_file(self, f):
        # Skip header
        while True:
            x = next(f)
            if x[0] != '#':
                break

        fieldnames = x
        fieldnames = fieldnames.split()

        reader = csv.reader(f, delimiter='\t')

        d = {}
        for row in reader:
            gene_id = row[0]
            d[gene_id] = {}
            for k, v in zip(fieldnames[1:], row[1:]):
                d[gene_id][k] = v

        return d
