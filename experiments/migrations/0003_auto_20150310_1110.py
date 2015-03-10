# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0002_auto_20150303_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='date',
            field=models.DateField(db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='temperature',
            field=models.DecimalField(max_digits=3, decimal_places=1, db_index=True),
            preserve_default=True,
        ),
    ]
