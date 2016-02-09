# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0003_merge_medical_categories'),
        ('core', '0009_remove_djcelery'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalcategory',
            name='users_for_expedited_review',
            field=models.ManyToManyField(related_name='expedited_review_categories', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunSQL('''
            insert into core_medicalcategory_users_for_expedited_review (user_id, medicalcategory_id)
                select ercu.user_id, mc.id
                from core_expeditedreviewcategory_users ercu
                inner join core_expeditedreviewcategory erc
                    on erc.id = ercu.expeditedreviewcategory_id
                inner join core_medicalcategory mc on mc.abbrev = erc.abbrev
        '''),
        migrations.RemoveField(
            model_name='expeditedreviewcategory',
            name='users',
        ),
        migrations.RenameField(
            model_name='submission',
            old_name='expedited_review_categories',
            new_name='old_expedited_review_categories',
        ),
        migrations.AddField(
            model_name='submission',
            name='expedited_review_categories',
            field=models.ManyToManyField(related_name='submissions_for_expedited_review', to='core.MedicalCategory', blank=True),
        ),
        migrations.RunSQL('''
            insert into core_submission_expedited_review_categories (submission_id, medicalcategory_id)
                select soerc.submission_id, mc.id
                from core_submission_old_expedited_review_categories soerc
                inner join core_expeditedreviewcategory erc
                    on erc.id = soerc.expeditedreviewcategory_id
                inner join core_medicalcategory mc on mc.abbrev = erc.abbrev
        '''),
        migrations.RemoveField(
            model_name='submission',
            name='old_expedited_review_categories',
        ),
        migrations.DeleteModel(
            name='ExpeditedReviewCategory',
        ),
    ]
