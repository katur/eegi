# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'LibraryWell.plate_id'
        db.delete_column('LibraryWell', 'plate_id_id')

        # Adding field 'LibraryWell.plate'
        db.add_column('LibraryWell', 'plate',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['library.LibraryPlate']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'LibraryWell.plate_id'
        db.add_column('LibraryWell', 'plate_id',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['library.LibraryPlate']),
                      keep_default=False)

        # Deleting field 'LibraryWell.plate'
        db.delete_column('LibraryWell', 'plate_id')


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
        u'library.librarywell': {
            'Meta': {'ordering': "['id']", 'object_name': 'LibraryWell', 'db_table': "'LibraryWell'"},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '24', 'primary_key': 'True'}),
            'intended_clone': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clones.Clone']", 'null': 'True', 'blank': 'True'}),
            'parent_well': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['library.LibraryWell']", 'null': 'True', 'blank': 'True'}),
            'plate': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['library.LibraryPlate']"}),
            'well': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        }
    }

    complete_apps = ['library']