# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Price'
        db.create_table('billing_price', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.SmallIntegerField')(unique=True, db_index=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('billing', ['Price'])


    def backwards(self, orm):
        
        # Deleting model 'Price'
        db.delete_table('billing_price')


    models = {
        'billing.price': {
            'Meta': {'object_name': 'Price'},
            'category': ('django.db.models.fields.SmallIntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['billing']
