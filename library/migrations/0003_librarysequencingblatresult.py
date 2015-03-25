# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0001_initial'),
        ('library', '0002_auto_20150304_1301'),
    ]

    operations = [
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
            bases=(models.Model,),
        ),
    ]
