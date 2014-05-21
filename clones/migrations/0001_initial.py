# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClonePlate',
            fields=[
                ('name', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('screen_stage', models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
