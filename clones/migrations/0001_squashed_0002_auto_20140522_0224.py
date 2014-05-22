# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [(b'clones', '0001_initial'), (b'clones', '0002_cloneplate_number_of_wells'), (b'clones', '0003_auto_20140522_0216'), (b'clones', '0002_auto_20140522_0224')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClonePlate',
            fields=[
                ('id', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('screen_stage', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('number_of_wells', models.PositiveSmallIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
