# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0005_auto_20150913_1029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devstarscore',
            name='well',
            field=models.CharField(max_length=3, db_index=True),
        ),
        migrations.AlterField(
            model_name='manualscore',
            name='well',
            field=models.CharField(max_length=3, db_index=True),
        ),
    ]
