# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0001_initial'),
        ('library', '0003_librarysequencingblatresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarywell',
            name='sequence_verified_clone',
            field=models.ForeignKey(related_name='seq_clone', default=None, blank=True, to='clones.Clone', null=True),
            preserve_default=True,
        ),
    ]
