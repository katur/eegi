# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloneplate',
            name='number_of_wells',
            field=models.PositiveSmallIntegerField(default=96),
            preserve_default=False,
        ),
    ]
