# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Experiment'
        db.create_table('Experiment', (
            ('id', self.gf('django.db.models.fields.PositiveIntegerField')(primary_key=True)),
            ('worm_strain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['worms.WormStrain'])),
            ('library_plate', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['library.LibraryPlate'])),
            ('temperature', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=1)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('is_junk', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'experiments', ['Experiment'])


    def backwards(self, orm):
        # Deleting model 'Experiment'
        db.delete_table('Experiment')


    models = {
        u'experiments.experiment': {
            'Meta': {'ordering': "['id']", 'object_name': 'Experiment', 'db_table': "'Experiment'"},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.PositiveIntegerField', [], {'primary_key': 'True'}),
            'is_junk': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'library_plate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['library.LibraryPlate']"}),
            'temperature': ('django.db.models.fields.DecimalField', [], {'max_digits': '3', 'decimal_places': '1'}),
            'worm_strain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['worms.WormStrain']"})
        },
        u'library.libraryplate': {
            'Meta': {'ordering': "['id']", 'object_name': 'LibraryPlate', 'db_table': "'LibraryPlate'"},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'number_of_wells': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'screen_stage': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'worms.wormstrain': {
            'Meta': {'ordering': "['genotype']", 'object_name': 'WormStrain', 'db_table': "'WormStrain'"},
            'allele': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'gene': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'genotype': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'on_wormbase': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'permissive_temperature': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1', 'blank': 'True'}),
            'restrictive_temperature': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1', 'blank': 'True'})
        }
    }

    complete_apps = ['experiments']