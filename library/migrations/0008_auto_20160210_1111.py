# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_librarysequencing_sample_well'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='librarysequencing',
            options={'ordering': ['sample_plate', 'sample_well']},
        ),
        migrations.RenameField(
            model_name='librarysequencing',
            old_name='sample_plate_name',
            new_name='sample_plate',
        ),
    ]
