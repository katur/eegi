# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clone',
            fields=[
                ('id', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('mapping_db_pk', models.IntegerField(null=True, blank=True)),
                ('library', models.CharField(max_length=30, blank=True)),
                ('clone_type', models.CharField(max_length=30, blank=True)),
                ('forward_primer', models.CharField(max_length=100, blank=True)),
                ('reverse_primer', models.CharField(max_length=100, blank=True)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'Clone',
            },
        ),
        migrations.CreateModel(
            name='CloneTarget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transcript_isoform', models.CharField(max_length=30, blank=True)),
                ('clone_amplicon_id', models.IntegerField()),
                ('amplicon_evidence', models.CharField(max_length=4)),
                ('amplicon_is_designed', models.BooleanField()),
                ('amplicon_is_unique', models.BooleanField()),
                ('length_span', models.IntegerField()),
                ('raw_score', models.IntegerField()),
                ('unique_raw_score', models.IntegerField()),
                ('relative_score', models.FloatField()),
                ('specificity_index', models.FloatField()),
                ('unique_chunk_index', models.FloatField()),
                ('is_on_target', models.BooleanField()),
                ('is_primary_target', models.BooleanField()),
                ('clone', models.ForeignKey(to='clones.Clone')),
            ],
            options={
                'db_table': 'CloneTarget',
            },
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('cosmid_id', models.CharField(max_length=30)),
                ('locus', models.CharField(max_length=30, blank=True)),
                ('gene_type', models.CharField(max_length=30, blank=True)),
                ('gene_class_description', models.TextField(blank=True)),
                ('functional_description', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'Gene',
            },
        ),
        migrations.AddField(
            model_name='clonetarget',
            name='gene',
            field=models.ForeignKey(to='clones.Gene'),
        ),
    ]
