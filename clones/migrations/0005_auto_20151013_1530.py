# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0004_auto_20151012_2353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clonealias',
            name='clone',
        ),
        migrations.RemoveField(
            model_name='genealias',
            name='gene',
        ),
        migrations.AddField(
            model_name='gene',
            name='functional_description',
            field=models.TextField(blank=True),
        ),
        migrations.DeleteModel(
            name='CloneAlias',
        ),
        migrations.DeleteModel(
            name='GeneAlias',
        ),
    ]
