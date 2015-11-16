# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0004_auto_20151116_1547'),
    ]

    operations = [
        migrations.RenameModel('ExperimentWell', 'Experiment'),

        migrations.AlterModelTable(name='experiment',
                                   table='Experiment'),

        migrations.RenameField('DevstarScore', 'experiment_well',
                               'experiment'),

        migrations.RenameField('ManualScore', 'experiment_well',
                               'experiment'),
    ]
