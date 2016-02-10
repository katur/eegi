# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_auto_20160209_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarysequencing',
            name='sample_well',
            field=models.CharField(max_length=3, blank=True),
        ),
    ]
