# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='librarywell',
            unique_together=set([('library_plate', 'well')]),
        ),
    ]
