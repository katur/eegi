# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wormstrains', '0001_squashed_0004_auto_20140520_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='wormstrain',
            name='on_wormbase',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
