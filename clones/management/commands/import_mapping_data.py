import MySQLdb

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from clones.models import Clone, Gene, CloneTarget
from eegi.localsettings import MAPPING_DATABASE
from utils.sql import get_field_dictionary
from utils.scripting import require_db_write_acknowledgement


class Command(BaseCommand):
    """
    Import clone-gene mapping data from Firoz's RNAiCloneMapper database.

    This script:

        - Does not add or delete rows in the Clone table, or touch the PK.
          However, it may update any of the other fields in this table.

        - Does not delete rows in the Gene table, or change the PK of
          existing rows. However, it may add new rows, and may update
          any of the other fields in this table.

        - Deletes all rows in the CloneTarget table, and creates
          this table from scratch. This is because, in addition
          to new or changed clone-gene mappings since the last time
          this command was run, there may be deleted mappings.
    """

    help = "Import RNAi clone mapping data from Firoz's database."

    def handle(self, **options):
        require_db_write_acknowledgement()

        mapping_db = MySQLdb.connect(host=MAPPING_DATABASE['HOST'],
                                     user=MAPPING_DATABASE['USER'],
                                     passwd=MAPPING_DATABASE['PASSWORD'],
                                     db=MAPPING_DATABASE['NAME'])

        cursor = mapping_db.cursor()

        # Get dictionary to translate from this database's pk to the
        #   mapping database pk
        pk_translator = _get_pk_translator(cursor)

        # Get all info from the mapping database
        all_mapping_clones = _get_all_mapping_clones(cursor)
        all_mapping_genes = _get_all_mapping_genes(cursor)
        all_mapping_targets = _get_all_mapping_targets(cursor)

        # Delete all Clone-to-Gene mappings from this database.
        CloneTarget.objects.all().delete()

        # Counters to keep track of no-target and multiple-target cases
        num_clones_no_targets = 0
        num_clones_multiple_targets = 0

        # Iterate over the clones in this table, updating all mapping info
        clones = Clone.objects.exclude(id='L4440')
        for clone in clones:
            num_targets = _process_clone(
                clone, pk_translator, all_mapping_clones,
                all_mapping_genes, all_mapping_targets)

            if num_targets == 0:
                num_clones_no_targets += 1

            elif num_targets > 1:
                num_clones_multiple_targets += 1

        self.stdout.write('{} clones with no targets.'
                          .format(num_clones_no_targets))
        self.stdout.write('{} clones with multiple targets.'
                          .format(num_clones_multiple_targets))


def _process_clone(clone, pk_translator, all_mapping_clones,
                   all_mapping_genes, all_mapping_targets):
    """
    Process this clone's mapping information.

    Returns the number of targets.
    """
    # Ensure exactly 1 PK for this clone in the mapping database
    try:
        mapping_pks = pk_translator[clone.pk]
    except KeyError:
        raise CommandError('No alias match for {}'.format(clone.pk))

    if len(mapping_pks) > 1:
        raise CommandError('>1 alias match for {}'.format(clone.pk))

    clone.mapping_db_pk = mapping_pks[0]

    # Update general information about this clone (e.g. its primers)
    clone_mapping_info = all_mapping_clones[clone.mapping_db_pk]
    _update_clone_info(clone, clone_mapping_info)

    # If there are no targets, move on
    try:
        mapping_targets = all_mapping_targets[clone.mapping_db_pk]

    except KeyError:
        return 0

    # If there are targets, update the gene and save a new gene-target mapping
    for target_mapping_info in mapping_targets:
        gene_id = target_mapping_info['gene_id']

        try:
            gene = Gene.objects.get(pk=gene_id)

        except ObjectDoesNotExist:
            # RNAiCloneMapper uses MyISAM tables which don't enforce FKs
            if gene_id not in all_mapping_genes:
                raise CommandError('ERROR: Gene {} from targets table not '
                                   'present in RNAiCloneMapper.Gene table'
                                   .format(gene_id))
            gene = Gene(id=gene_id)

        gene_mapping_info = all_mapping_genes[gene_id]
        _update_gene_info(gene, gene_mapping_info)
        _add_target(clone, target_mapping_info)

    return len(mapping_targets)


def _get_pk_translator(cursor):
    """
    Get a dictionary to translate mapping_alias to mapping_pk.

    This can be used to translate this database's pk to the mapping pk.
    """
    query = 'SELECT alias, clone_id FROM CloneAlias'

    cursor.execute(query)

    rows = cursor.fetchall()

    mapping_alias_to_pk = {}

    for row in rows:
        alias, mapping_pk = row
        if alias not in mapping_alias_to_pk:
            mapping_alias_to_pk[alias] = []

        if mapping_pk not in mapping_alias_to_pk[alias]:
            mapping_alias_to_pk[alias].append(mapping_pk)

    return mapping_alias_to_pk


def _get_all_mapping_clones(cursor):
    """
    Get dictionary of all clones from the mapping database.

    This dictionary is keyed on the clone's pk in the mapping
    database.

    The value is a dictionary of fieldname:value pairs in the
    mapping database.
    """
    fieldnames = ['id', 'library', 'clone_type', 'forward_primer',
                  'reverse_primer']
    return get_field_dictionary(cursor, 'Clone', fieldnames)


def _get_all_mapping_genes(cursor):
    """
    Get dictionary of all genes from the mapping database.

    This dictionary is keyed on the gene's pk in the mapping
    database.

    The value is a dictionary of fieldname:value pairs in the
    mapping database.
    """
    fieldnames = ['id', 'cosmid_id', 'locus', 'gene_type']
    return get_field_dictionary(cursor, 'Gene', fieldnames)


def _get_all_mapping_targets(cursor):
    """
    Get dictionary of all targets from the mapping database.

    This dictionary is keyed on the clone's pk in the mapping database.

    The value is a list. Each item in this list is a dictionary
    capturing the fieldname:value pairs about one target of this clone.
    """
    fieldnames = [
        'clone_id', 'id', 'clone_amplicon_id',
        'amplicon_evidence', 'amplicon_is_designed',
        'amplicon_is_unique',
        'gene_id', 'transcript_isoform',
        'length_span', 'raw_score', 'unique_raw_score',
        'relative_score', 'specificity_index', 'unique_chunk_index',
        'is_on_target', 'is_primary_target'
    ]

    fieldnames_as_string = ', '.join(fieldnames)
    query = 'SELECT {} FROM CloneTarget'.format(fieldnames_as_string)
    cursor.execute(query)
    rows = cursor.fetchall()

    all_targets = {}
    for row in rows:
        clone_pk = row[0]
        if clone_pk not in all_targets:
            all_targets[clone_pk] = []

        this_target = {}
        for k, v in zip(fieldnames[1:], row[1:]):
            this_target[k] = v

        all_targets[clone_pk].append(this_target)

    return all_targets


def _update_clone_info(clone, clone_mapping_info):
    """
    Update clone's fields according to the clone_mapping_info dictionary.
    """
    clone.library = clone_mapping_info['library']
    clone.clone_type = clone_mapping_info['clone_type']
    clone.forward_primer = clone_mapping_info['forward_primer']
    clone.reverse_primer = clone_mapping_info['reverse_primer']
    clone.save()


def _update_gene_info(gene, gene_mapping_info):
    """
    Update gene's fields according to the gene_mapping_info dictionary.
    """
    gene.cosmid_id = gene_mapping_info['cosmid_id']
    gene.locus = gene_mapping_info['locus']
    if gene.locus == 'NA':
        gene.locus = ''
    gene.gene_type = gene_mapping_info['gene_type']
    gene.save()


def _add_target(clone, target_mapping_info):
    """
    Add a new CloneTarget to the database, representing clone targeting gene,
    and with other fields specified in dictionary target_mapping_info.
    """
    # Keep the target PK consistent between this database and the
    # RNAiCloneMapper database
    target_id = target_mapping_info['id']

    if CloneTarget.objects.filter(id=target_id):
        raise CommandError('ERROR: all CloneTargets should have been deleted '
                           'from the database at the start of this command')

    target = CloneTarget(clone=clone, **target_mapping_info)
    target.save()
