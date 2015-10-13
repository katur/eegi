# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0003_auto_20151012_2352'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='clonealias',
            table='CloneAlias',
        ),
        migrations.AlterModelTable(
            name='clonetarget',
            table='CloneTarget',
        ),
        migrations.AlterModelTable(
            name='gene',
            table='Gene',
        ),
        migrations.AlterModelTable(
            name='genealias',
            table='GeneAlias',
        ),
    ]
