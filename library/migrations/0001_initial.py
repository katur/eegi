# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LibraryPlate'
        db.create_table('LibraryPlate', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('screen_stage', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('number_of_wells', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'library', ['LibraryPlate'])


    def backwards(self, orm):
        # Deleting model 'LibraryPlate'
        db.delete_table('LibraryPlate')


    models = {
        u'library.libraryplate': {
            'Meta': {'ordering': "['id']", 'object_name': 'LibraryPlate', 'db_table': "'LibraryPlate'"},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            'number_of_wells': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'screen_stage': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['library']