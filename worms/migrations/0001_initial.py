# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WormStrain',
            fields=[
                ('id', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('gene', models.CharField(max_length=10, blank=True)),
                ('allele', models.CharField(max_length=10, blank=True)),
                ('genotype', models.CharField(max_length=20, blank=True)),
                ('permissive_temperature', models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True)),
                ('restrictive_temperature', models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True)),
            ],
            options={
                'ordering': ['genotype'],
                'db_table': 'WormStrain',
            },
            bases=(models.Model,),
        ),
    ]
