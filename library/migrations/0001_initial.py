# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibraryPlate',
            fields=[
                ('id', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('number_of_wells', models.PositiveSmallIntegerField()),
                ('screen_stage', models.PositiveSmallIntegerField(db_index=True, null=True, blank=True)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'LibraryPlate',
            },
        ),
        migrations.CreateModel(
            name='LibrarySequencing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample_plate_name', models.CharField(max_length=10, blank=True)),
                ('sample_tube_number', models.IntegerField(null=True, blank=True)),
                ('genewiz_tracking_number', models.CharField(max_length=20, null=True, blank=True)),
                ('genewiz_tube_label', models.CharField(max_length=20, null=True, blank=True)),
                ('sequence', models.TextField(blank=True)),
                ('ab1_filename', models.CharField(max_length=20, null=True, blank=True)),
                ('quality_score', models.IntegerField(null=True, blank=True)),
                ('crl', models.IntegerField(null=True, blank=True)),
                ('qv20plus', models.IntegerField(null=True, blank=True)),
                ('si_a', models.IntegerField(null=True, blank=True)),
                ('si_t', models.IntegerField(null=True, blank=True)),
                ('si_c', models.IntegerField(null=True, blank=True)),
                ('si_g', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['sample_plate_name', 'sample_tube_number'],
                'db_table': 'LibrarySequencing',
            },
        ),
        migrations.CreateModel(
            name='LibrarySequencingBlatResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('e_value', models.FloatField()),
                ('bit_score', models.IntegerField()),
                ('hit_rank', models.PositiveSmallIntegerField()),
                ('clone_hit', models.ForeignKey(to='clones.Clone')),
                ('library_sequencing', models.ForeignKey(to='library.LibrarySequencing')),
            ],
            options={
                'ordering': ['library_sequencing', 'hit_rank'],
                'db_table': 'LibrarySequencingBlatResult',
            },
        ),
        migrations.CreateModel(
            name='LibraryStock',
            fields=[
                ('id', models.CharField(max_length=24, serialize=False, primary_key=True)),
                ('well', models.CharField(max_length=3)),
                ('intended_clone', models.ForeignKey(blank=True, to='clones.Clone', null=True)),
                ('parent_stock', models.ForeignKey(blank=True, to='library.LibraryStock', null=True)),
                ('plate', models.ForeignKey(related_name='wells', to='library.LibraryPlate')),
                ('sequence_verified_clone', models.ForeignKey(related_name='seq_clone', default=None, blank=True, to='clones.Clone', null=True)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'LibraryStock',
            },
        ),
        migrations.AddField(
            model_name='librarysequencing',
            name='source_stock',
            field=models.ForeignKey(blank=True, to='library.LibraryStock', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='librarystock',
            unique_together=set([('plate', 'well')]),
        ),
        migrations.AlterUniqueTogether(
            name='librarysequencing',
            unique_together=set([('genewiz_tracking_number', 'genewiz_tube_label')]),
        ),
    ]
