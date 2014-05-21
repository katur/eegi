# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wormstrains', '0002_wormstrain_on_wormbase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wormstrain',
            name='allele',
            field=models.CharField(max_length=10, blank=True),
        ),
        migrations.AlterField(
            model_name='wormstrain',
            name='genotype',
            field=models.CharField(max_length=20, blank=True),
        ),
    ]
