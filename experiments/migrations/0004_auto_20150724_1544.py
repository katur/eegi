# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0003_auto_20150310_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devstarscore',
            name='count_embryo',
            field=models.IntegerField(help_text=b'area_embryo // 70', null=True, blank=True),
        ),
    ]
