# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experiment',
            name='is_junk',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='experiment',
            name='screen_level',
            field=models.PositiveSmallIntegerField(db_index=True),
            preserve_default=True,
        ),
    ]
