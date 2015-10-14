# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clones', '0006_gene_gene_class_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clonetarget',
            name='clone',
        ),
        migrations.AddField(
            model_name='clonetarget',
            name='clone',
            field=models.ForeignKey(to='clones.Clone'),
        ),
    ]
