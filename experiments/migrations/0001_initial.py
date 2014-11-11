# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library', '0001_initial'),
        ('worms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevstarScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('well', models.CharField(max_length=3)),
                ('area_adult', models.IntegerField(help_text=b'DevStaR program output', null=True, blank=True)),
                ('area_larva', models.IntegerField(help_text=b'DevStaR program output', null=True, blank=True)),
                ('area_embryo', models.IntegerField(help_text=b'DevStaR program output', null=True, blank=True)),
                ('count_adult', models.IntegerField(help_text=b'DevStaR program output', null=True, blank=True)),
                ('count_larva', models.IntegerField(help_text=b'DevStaR program output', null=True, blank=True)),
                ('count_embryo', models.IntegerField(help_text=b'area_embryo / 70', null=True, blank=True)),
                ('larva_per_adult', models.FloatField(default=None, help_text=b'count_larva / count_adult', null=True, blank=True)),
                ('embryo_per_adult', models.FloatField(default=None, help_text=b'count_embryo / count_adult', null=True, blank=True)),
                ('survival', models.FloatField(default=None, help_text=b'count_larva / (count_larva + count_embryo)', null=True, blank=True)),
                ('lethality', models.FloatField(default=None, help_text=b'count_embryo / (count_larva + count_embryo)', null=True, blank=True)),
                ('is_bacteria_present', models.NullBooleanField(default=None, help_text=b'DevStaR program output')),
                ('selected_for_scoring', models.NullBooleanField(default=None)),
                ('gi_score_larva_per_adult', models.FloatField(default=None, null=True, blank=True)),
                ('gi_score_survival', models.FloatField(default=None, null=True, blank=True)),
            ],
            options={
                'db_table': 'DevstarScore',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('library_plate_copy_number', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('screen_level', models.PositiveSmallIntegerField()),
                ('temperature', models.DecimalField(max_digits=3, decimal_places=1)),
                ('date', models.DateField()),
                ('is_junk', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
                ('library_plate', models.ForeignKey(to='library.LibraryPlate')),
                ('worm_strain', models.ForeignKey(to='worms.WormStrain')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'Experiment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManualScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('well', models.CharField(max_length=3)),
                ('timestamp', models.DateTimeField()),
                ('experiment', models.ForeignKey(to='experiments.Experiment')),
            ],
            options={
                'db_table': 'ManualScore',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManualScoreCode',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=100, blank=True)),
                ('short_description', models.CharField(max_length=50, blank=True)),
                ('legacy_description', models.CharField(max_length=100, blank=True)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'ManualScoreCode',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='manualscore',
            name='score_code',
            field=models.ForeignKey(to='experiments.ManualScoreCode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='manualscore',
            name='scorer',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='devstarscore',
            name='experiment',
            field=models.ForeignKey(to='experiments.Experiment'),
            preserve_default=True,
        ),
    ]
