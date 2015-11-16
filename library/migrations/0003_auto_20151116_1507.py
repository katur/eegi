# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_auto_20151112_1619'),
    ]

    operations = [
        migrations.RenameField(
            model_name='librarywell',
            old_name='library_plate',
            new_name='plate',
        ),
        migrations.AlterUniqueTogether(
            name='librarywell',
            unique_together=set([('plate', 'well')]),
        ),
    ]
