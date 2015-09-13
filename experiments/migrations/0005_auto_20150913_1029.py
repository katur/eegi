# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0004_auto_20150724_1544'),
    ]

    operations = [
        migrations.RenameField(
            model_name='experiment',
            old_name='screen_level',
            new_name='screen_stage',
        ),
    ]
