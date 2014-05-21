# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wormstrains', '__first__'),
        ('clones', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True)),
                ('worm_strain', models.ForeignKey(to='wormstrains.WormStrain', to_field=b'name')),
                ('clone_plate', models.ForeignKey(to='clones.ClonePlate', to_field=b'name')),
                ('temperature', models.DecimalField(max_digits=3, decimal_places=1)),
                ('date', models.DateField()),
                ('is_junk', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
