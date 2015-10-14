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
            num_mismatches = 0

            # Does WormBase molecular_name align with Firoz's database?
            wb_molecular = info['molecular_name']
            firoz_cosmid = gene.cosmid_id
            if (not wb_molecular.startswith(firoz_cosmid)):
                num_mismatches += 1
                self.stdout.write('Molecular/cosmid mismatch for {}: '
                                  'WormBase says {}, Firoz says {}'
                                  .format(gene, wb_molecular, firoz_cosmid))

            # Does WormBase public_name align with Firoz's database?
            wb_public = info['public_name']
            firoz_locus = gene.locus
            if (wb_public != firoz_locus and
                    not (firoz_locus == '' and wb_public == firoz_cosmid)):
                num_mismatches += 1
                self.stdout.write('Public/locus mismatch for {}: '
                                  'WormBase says {}, Firoz says {}'
                                  .format(gene, wb_public, firoz_locus))

            description = info['concise_description']
            gene.functional_description = description
            gene.save()

        if num_mismatches:
            self.stdout.write('Total number mismatches: {}'
                              .format(num_mismatches))

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
