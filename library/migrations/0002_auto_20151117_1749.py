# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='librarysequencingblatresult',
            options={'ordering': ['sequencing', 'hit_rank']},
        ),
        migrations.RenameField(
            model_name='librarysequencingblatresult',
            old_name='library_sequencing',
            new_name='sequencing',
        ),
        migrations.AlterField(
            model_name='librarystock',
            name='plate',
            field=models.ForeignKey(to='library.LibraryPlate'),
        ),
    ]
