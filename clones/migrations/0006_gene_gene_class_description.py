# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0005_auto_20151013_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='gene',
            name='gene_class_description',
            field=models.TextField(blank=True),
        ),
    ]
