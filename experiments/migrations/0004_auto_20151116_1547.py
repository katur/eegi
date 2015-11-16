# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0003_auto_20151116_1507'),
    ]

    operations = [
        migrations.RenameField(
            model_name='experimentwell',
            old_name='experiment_plate',
            new_name='plate',
        ),
        migrations.AlterUniqueTogether(
            name='experimentwell',
            unique_together=set([('plate', 'well')]),
        ),
    ]
