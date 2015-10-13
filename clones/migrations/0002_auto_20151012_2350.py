# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CloneAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=30)),
                ('alias_type', models.CharField(max_length=30, blank=True)),
                ('source', models.CharField(max_length=30, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='CloneTarget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('clone_amplicon_id', models.IntegerField()),
                ('amplicon_evidence', models.CharField(max_length=4)),
                ('amplicon_is_designed', models.BooleanField()),
                ('amplicon_is_unique', models.BooleanField()),
                ('transcript_isoform', models.CharField(max_length=30, blank=True)),
                ('length_span', models.IntegerField()),
                ('raw_score', models.IntegerField()),
                ('unique_raw_score', models.IntegerField()),
                ('relative_score', models.FloatField()),
                ('specificity_index', models.FloatField()),
                ('unique_chunk_index', models.FloatField()),
                ('is_on_target', models.BooleanField()),
                ('is_primary_target', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('cosmid_id', models.CharField(max_length=30)),
                ('locus', models.CharField(max_length=30, blank=True)),
                ('gene_type', models.CharField(max_length=30, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GeneAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(max_length=100)),
                ('alias_type', models.CharField(max_length=100, blank=True)),
                ('functional_description', models.TextField(blank=True)),
                ('gene', models.ForeignKey(to='clones.Gene')),
            ],
        ),
        migrations.AddField(
            model_name='clone',
            name='clone_type',
            field=models.CharField(max_length=30, blank=True),
        ),
        migrations.AddField(
            model_name='clone',
            name='forward_primer',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='clone',
            name='library',
            field=models.CharField(max_length=30, blank=True),
        ),
        migrations.AddField(
            model_name='clone',
            name='mapping_db_pk',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='clone',
            name='reverse_primer',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='clonetarget',
            name='clone',
            field=models.ForeignKey(to='clones.Clone'),
        ),
        migrations.AddField(
            model_name='clonetarget',
            name='gene',
            field=models.ForeignKey(to='clones.Gene'),
        ),
        migrations.AddField(
            model_name='clonealias',
            name='clone',
            field=models.ForeignKey(to='clones.Clone'),
        ),
    ]
