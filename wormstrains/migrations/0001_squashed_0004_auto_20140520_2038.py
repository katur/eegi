# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [(b'wormstrains', '0001_initial'), (b'wormstrains', '0002_auto_20140520_2031'), (b'wormstrains', '0003_auto_20140520_2032'), (b'wormstrains', '0004_auto_20140520_2038')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WormStrain',
            fields=[
                ('name', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('gene', models.CharField(max_length=10, blank=True)),
                ('allele', models.CharField(unique=True, max_length=10, blank=True)),
                ('genotype', models.CharField(unique=True, max_length=20, blank=True)),
                ('restrictive_temperature', models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True)),
                ('permissive_temperature', models.DecimalField(null=True, max_digits=3, decimal_places=1, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
