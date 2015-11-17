# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='devstarscore',
            options={'ordering': ['experiment']},
        ),
        migrations.AlterModelOptions(
            name='experiment',
            options={'ordering': ['plate', 'well']},
        ),
        migrations.AlterModelOptions(
            name='manualscore',
            options={'ordering': ['experiment', 'scorer', 'timestamp', 'score_code']},
        ),
    ]
