# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'WormStrain.on_wormbase'
        db.delete_column('WormStrain', 'on_wormbase')


    def backwards(self, orm):
        # Adding field 'WormStrain.on_wormbase'
        db.add_column('WormStrain', 'on_wormbase',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    models = {
        u'worms.wormstrain': {
            'Meta': {'ordering': "['genotype']", 'object_name': 'WormStrain', 'db_table': "'WormStrain'"},
            'allele': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'gene': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'genotype': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'permissive_temperature': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1', 'blank': 'True'}),
            'restrictive_temperature': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1', 'blank': 'True'})
        }
    }

    complete_apps = ['worms']