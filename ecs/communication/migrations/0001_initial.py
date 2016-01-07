from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('unread', models.BooleanField(default=True)),
                ('soft_bounced', models.BooleanField(default=False)),
                ('text', models.TextField()),
                ('rawmsg', models.TextField(null=True)),
                ('rawmsg_msgid', models.CharField(max_length=250, null=True, db_index=True)),
                ('rawmsg_digest_hex', models.CharField(max_length=32, null=True, db_index=True)),
                ('origin', models.SmallIntegerField(default=1, choices=[(1, 'Alice'), (2, 'Bob')])),
                ('smtp_delivery_state', models.CharField(default='new', max_length=7, db_index=True, choices=[('new', 'new'), ('received', 'received'), ('pending', 'pending'), ('started', 'started'), ('success', 'success'), ('failure', 'failure'), ('retry', 'retry'), ('revoked', 'revoked')])),
                ('uuid', models.CharField(max_length=32, db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('closed_by_sender', models.BooleanField(default=False)),
                ('closed_by_receiver', models.BooleanField(default=False)),
                ('last_message', models.OneToOneField(related_name='head', null=True, to='communication.Message')),
                ('receiver', models.ForeignKey(related_name='incoming_threads', to=settings.AUTH_USER_MODEL)),
                ('related_thread', models.ForeignKey(to='communication.Thread', null=True)),
                ('sender', models.ForeignKey(related_name='outgoing_threads', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
