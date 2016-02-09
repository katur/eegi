# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_auto_20160208_1213'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarysequencing',
            name='genewiz_order_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
