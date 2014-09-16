# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Clone'
        db.create_table('RNAiClone', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=30, primary_key=True)),
        ))
        db.send_create_signal(u'clones', ['Clone'])


    def backwards(self, orm):
        # Deleting model 'Clone'
        db.delete_table('RNAiClone')


    models = {
        u'clones.clone': {
            'Meta': {'ordering': "['id']", 'object_name': 'Clone', 'db_table': "'RNAiClone'"},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '30', 'primary_key': 'True'})
        }
    }

    complete_apps = ['clones']