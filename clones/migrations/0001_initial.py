# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clone',
            fields=[
                ('id', models.CharField(max_length=30, serialize=False, primary_key=True)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'RNAiClone',
            },
            bases=(models.Model,),
        ),
    ]
