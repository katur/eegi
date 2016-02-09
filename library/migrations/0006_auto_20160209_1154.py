# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_librarysequencing_genewiz_order_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='librarysequencing',
            name='ab1_filename',
            field=models.CharField(default='', max_length=20, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarysequencing',
            name='genewiz_tracking_number',
            field=models.CharField(default='', max_length=20, blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='librarysequencing',
            name='genewiz_tube_label',
            field=models.CharField(default='', max_length=20, blank=True),
            preserve_default=False,
        ),
    ]
