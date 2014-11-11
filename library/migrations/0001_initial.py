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
                ('screen_stage', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('number_of_wells', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'LibraryPlate',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LibrarySequencing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('library_plate_copy_number', models.PositiveSmallIntegerField(null=True, blank=True)),
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
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LibraryWell',
            fields=[
                ('id', models.CharField(max_length=24, serialize=False, primary_key=True)),
                ('well', models.CharField(max_length=3)),
                ('intended_clone', models.ForeignKey(blank=True, to='clones.Clone', null=True)),
                ('parent_library_well', models.ForeignKey(blank=True, to='library.LibraryWell', null=True)),
                ('plate', models.ForeignKey(to='library.LibraryPlate')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'LibraryWell',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='librarysequencing',
            name='source_library_well',
            field=models.ForeignKey(blank=True, to='library.LibraryWell', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='librarysequencing',
            unique_together=set([('genewiz_tracking_number', 'genewiz_tube_label')]),
        ),
    ]
