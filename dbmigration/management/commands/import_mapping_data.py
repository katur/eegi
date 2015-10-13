import MySQLdb

from django.core.management.base import BaseCommand

from clones.models import Clone
from eegi.local_settings import MAPPING_DATABASE
from utils.scripting import require_db_write_acknowledgement

HELP = '''
Import clone data from Firoz's RNAiCloneMapper database.
'''


class Command(BaseCommand):
    help = HELP

    def handle(self, **options):
        require_db_write_acknowledgement()

        mapping_db = MySQLdb.connect(host=MAPPING_DATABASE['HOST'],
                                     user=MAPPING_DATABASE['USER'],
                                     passwd=MAPPING_DATABASE['PASSWORD'],
                                     db=MAPPING_DATABASE['NAME'])
        self.cursor = mapping_db.cursor()

        clones = Clone.objects.all()

        for clone in clones:
            mapping_pk = self.get_mapping_pk(clone)
            self.add_clone_fields(clone, mapping_pk)
            self.add_clone_aliases(clone)
            self.add_clone_mappings(clone)

    def add_clone_aliases(self, clone):
        pass

    def add_clone_mappings(self, clone):
        pass

    def add_clone_fields(self, clone, mapping_pk):
        self.cursor.execute('SELECT id, library, clone_type, '
                            'forward_primer, reverse_primer '
                            'FROM Clone '
                            'WHERE id = %s'.format(mapping_pk))
        rows = self.cursor.fetchall()

        if len(rows) > 1:
            self.exit('>1 clone match for mapping clone pk %s'
                      .format(mapping_pk))
        elif len(rows) < 1:
            self.exit('No clone match for mapping clone pk %s'
                      .format(mapping_pk))

        row = rows[0]
        clone.mapping_db_pk = mapping_pk
        clone.library = row[1]
        clone.clone_type = row[2]
        clone.forward_primer = row[3]
        clone.reverse_primer = row[4]
        # clone.save()

    def get_mapping_pk(self, clone):
        self.cursor.execute('SELECT clone_id FROM CloneAlias '
                            'WHERE alias = `%s`'.format(clone.pk))
        rows = self.cursor.fetchall()

        if len(rows) > 1:
            self.exit('>1 alias match for %s'.format(clone.pk))
        elif len(rows) < 1:
            self.exit('No alias match for %s'.format(clone.pk))

        return rows[0]
