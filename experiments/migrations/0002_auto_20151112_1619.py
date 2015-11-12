# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='experimentwell',
            unique_together=set([('experiment_plate', 'well')]),
        ),
    ]
