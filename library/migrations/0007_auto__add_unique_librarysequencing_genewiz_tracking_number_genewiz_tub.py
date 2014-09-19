# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'LibrarySequencing', fields ['genewiz_tracking_number', 'genewiz_tube_label']
        db.create_unique('LibrarySequencing', ['genewiz_tracking_number', 'genewiz_tube_label'])


    def backwards(self, orm):
        # Removing unique constraint on 'LibrarySequencing', fields ['genewiz_tracking_number', 'genewiz_tube_label']
        db.delete_unique('LibrarySequencing', ['genewiz_tracking_number', 'genewiz_tube_label'])


    models = {
        u'clones.clone': {
            'Meta': {'ordering': "['id']", 'object_name': 'Clone', 'db_table': "'RNAiClone'"},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'})
        },
        u'library.libraryplate': {
            'Meta': {'ordering': "['id']", 'object_name': 'LibraryPlate', 'db_table': "'LibraryPlate'"},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'number_of_wells': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'screen_stage': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'library.librarysequencing': {
            'Meta': {'ordering': "['sample_plate_name', 'sample_tube_number']", 'unique_together': "(('genewiz_tracking_number', 'genewiz_tube_label'),)", 'object_name': 'LibrarySequencing', 'db_table': "'LibrarySequencing'"},
            'ab1_filename': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'crl': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'genewiz_tracking_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'genewiz_tube_label': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'library_plate_copy_number': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quality_score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'qv20plus': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sample_plate_name': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'sample_tube_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sequence': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'si_a': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'si_c': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'si_g': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'si_t': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'source_library_well': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['library.LibraryWell']", 'null': 'True', 'blank': 'True'})
        },
        u'library.librarywell': {
            'Meta': {'ordering': "['id']", 'object_name': 'LibraryWell', 'db_table': "'LibraryWell'"},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '24', 'primary_key': 'True'}),
            'intended_clone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clones.Clone']", 'null': 'True', 'blank': 'True'}),
            'parent_library_well': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['library.LibraryWell']", 'null': 'True', 'blank': 'True'}),
            'plate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['library.LibraryPlate']"}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        }
    }

    complete_apps = ['library']