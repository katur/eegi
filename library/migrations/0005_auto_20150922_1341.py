# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_librarywell_sequence_verified_clone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='librarywell',
            name='well',
            field=models.CharField(max_length=3, db_index=True),
        ),
    ]
