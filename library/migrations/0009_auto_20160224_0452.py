# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-24 09:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0008_auto_20160210_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='librarysequencing',
            name='source_stock',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.LibraryStock'),
        ),
        migrations.AlterField(
            model_name='librarystock',
            name='intended_clone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='clones.Clone'),
        ),
        migrations.AlterField(
            model_name='librarystock',
            name='parent_stock',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.LibraryStock'),
        ),
        migrations.AlterField(
            model_name='librarystock',
            name='sequence_verified_clone',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='seq_clone', to='clones.Clone'),
        ),
    ]
