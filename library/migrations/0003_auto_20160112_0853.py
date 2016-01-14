# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_auto_20151117_1749'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='libraryplate',
            options={'ordering': ['screen_stage', 'id']},
        ),
    ]
