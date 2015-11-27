from django.test import TestCase
from clones.models import Clone, Gene, CloneTarget


class CloneTestCase(TestCase):
    def setUp(self):
        Clone.objects.create(id='L4440')

        # clone_a targets gene_1 and gene_2
        clone_a = Clone.objects.create(id='sjj_a')

        # clone_b targets gene_2 and gene_3
        clone_b = Clone.objects.create(id='sjj_b')

        gene_1 = Gene.objects.create(
            id='WBGene1', cosmid_id='F4932.3', locus='gene-1')

        gene_2 = Gene.objects.create(
            id='WBGene2', cosmid_id='C653.2', locus='gene-2')

        gene_3 = Gene.objects.create(
            id='WBGene3', cosmid_id='P3421T.2', locus='gene-3')

        clone_target_kwargs = {
            'clone_amplicon_id': 54,
            'amplicon_evidence': '0011',
            'length_span': 434,
            'raw_score': 23,
            'unique_raw_score': 23,
            'relative_score': .6,
            'specificity_index': .4,
            'unique_chunk_index': .3,
            'amplicon_is_designed': True,
            'amplicon_is_unique': True,
            'is_on_target': True,
            'is_primary_target': True
        }

        CloneTarget.objects.create(
            clone=clone_a, gene=gene_1, **clone_target_kwargs)

        CloneTarget.objects.create(
            clone=clone_a, gene=gene_2, **clone_target_kwargs)

        CloneTarget.objects.create(
            clone=clone_b, gene=gene_2, **clone_target_kwargs)

        CloneTarget.objects.create(
            clone=clone_b, gene=gene_3, **clone_target_kwargs)

    def test_clone_is_control(self):
        l4440 = Clone.objects.get(pk='L4440')
        other = Clone.objects.get(pk='sjj_a')
        self.assertTrue(l4440.is_control())
        self.assertFalse(other.is_control())

    def test_get_targets(self):
        clone_a = Clone.objects.get(pk='sjj_a')
        clone_b = Clone.objects.get(pk='sjj_b')
        genes_a = [x.gene for x in clone_a.get_targets()]
        genes_b = [x.gene for x in clone_b.get_targets()]

        self.assertIn(Gene.objects.get(pk='WBGene1'), genes_a)
        self.assertIn(Gene.objects.get(pk='WBGene2'), genes_a)
        self.assertNotIn(Gene.objects.get(pk='WBGene3'), genes_a)

        self.assertNotIn(Gene.objects.get(pk='WBGene1'), genes_b)
        self.assertIn(Gene.objects.get(pk='WBGene2'), genes_b)
        self.assertIn(Gene.objects.get(pk='WBGene3'), genes_b)
