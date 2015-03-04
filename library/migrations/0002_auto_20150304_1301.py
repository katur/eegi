# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryplate',
            name='screen_stage',
            field=models.PositiveSmallIntegerField(db_index=True, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='librarywell',
            name='plate',
            field=models.ForeignKey(related_name='wells', to='library.LibraryPlate'),
            preserve_default=True,
        ),
    ]
