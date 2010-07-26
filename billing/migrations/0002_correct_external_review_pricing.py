# encoding: utf-8
import datetime
import decimal
from south.db import db
from south.v2 import DataMigration
from django.db import models
from ecs.billing.models import EXTERNAL_REVIEW_PRICING

class Migration(DataMigration):

    def forwards(self, orm):
        orm.Price.objects.filter(category=EXTERNAL_REVIEW_PRICING).update(price=decimal.Decimal("181.68"))

    def backwards(self, orm):
        "Write your backwards methods here."


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
