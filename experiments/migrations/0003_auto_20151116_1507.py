# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0002_auto_20151112_1619'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='manualscore',
            options={'ordering': ['scorer', 'timestamp', 'score_code']},
        ),
    ]
