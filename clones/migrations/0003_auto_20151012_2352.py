# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0002_auto_20151012_2350'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='clone',
            table='Clone',
        ),
    ]
