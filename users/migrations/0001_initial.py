# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    depends_on = (
        ('core', '0026_auto__add_field_assignedmedicalcategory_board_member__chg_field_submis'),
    )

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass


    models = {
        
    }

    complete_apps = ['users']
