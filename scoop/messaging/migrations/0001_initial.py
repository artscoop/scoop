# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import picklefield.fields
from django.conf import settings
from django.db import migrations, models

import scoop.core.util.data.dateutil


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('access', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('level', models.SmallIntegerField(default=0, choices=[[0, 'Warning'], [1, 'Important'], [2, 'Security']], verbose_name='Level', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2)])),
                ('title', models.CharField(max_length=80, verbose_name='Title')),
                ('text', models.TextField(verbose_name='Text')),
                ('items', models.CharField(default=b'', max_length=128, verbose_name='Items')),
                ('read', models.BooleanField(default=False, db_index=True, verbose_name='Read')),
                ('read_time', models.DateTimeField(default=None, null=True, verbose_name='Read', db_index=True)),
                ('user', models.ForeignKey(related_name='alerts_received', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
                'verbose_name': 'alert',
                'verbose_name_plural': 'alerts',
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('name', models.CharField(db_index=True, max_length=40, verbose_name='Name', validators=[django.core.validators.RegexValidator(b'^[\\d\\w][\\d\\s\\w]*$', 'Must contain only letters and digits')])),
                ('user', models.ForeignKey(related_name='thread_labels', verbose_name='Author', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'label',
                'verbose_name_plural': 'labels',
            },
        ),
        migrations.CreateModel(
            name='MailEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=128, unique=True, max_length=22, editable=False)),
                ('queued', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Queue time')),
                ('forced', models.BooleanField(default=False, db_index=True, verbose_name='Force sending')),
                ('sent', models.BooleanField(default=False, db_index=True, verbose_name='Sent')),
                ('sent_time', models.DateTimeField(default=None, null=True, verbose_name='Delivery time')),
                ('sent_email', models.CharField(default='', max_length=96, verbose_name='Email used')),
                ('minimum_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Minimum delivery')),
                ('recipient', models.ForeignKey(related_name='mailevents_to', verbose_name='Recipient', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'mail event',
                'verbose_name_plural': 'mail events',
            },
        ),
        migrations.CreateModel(
            name='MailType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(max_length=32, verbose_name='Codename')),
                ('template', models.CharField(help_text='Template filename without path and extension', max_length=32, verbose_name='Template')),
                ('interval', models.IntegerField(default=0, help_text='Delay in minutes', verbose_name='Minimum delay', choices=[[0, 'As soon as possible'], [5, 'Every 5 minutes'], [10, 'Every 10 minutes'], [30, 'Every 30 minutes'], [60, 'Every hour'], [720, 'Every 12 hours'], [1440, 'Every day'], [4320, 'Every 3 days'], [10080, 'Every week'], [43200, 'Every 30 days']])),
            ],
            options={
                'verbose_name': 'mail type',
                'verbose_name_plural': 'mail types',
            },
        ),
        migrations.CreateModel(
            name='MailTypeTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=15, verbose_name='language', choices=[(b'en', 'English'), (b'fr', 'French')])),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('model', models.ForeignKey(related_name='translations', verbose_name=b'mailtype', to='messaging.MailType')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('text', models.TextField(verbose_name='Text')),
                ('spam', models.FloatField(default=0.0, verbose_name='Spam level', validators=[django.core.validators.MaxValueValidator(1.0), django.core.validators.MinValueValidator(0.0)])),
                ('deleted', models.BooleanField(default=False, db_index=True, verbose_name='Deleted')),
                ('author', models.ForeignKey(related_name='messages_sent', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Author', to=settings.AUTH_USER_MODEL, null=True)),
                ('ip', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='IP', to='access.IP', null=True)),
            ],
            options={
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
                'permissions': (('can_force_send', 'Can force send messages'), ('can_broadcast', 'Can broadcast messages')),
            },
        ),
        migrations.CreateModel(
            name='Negotiation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('status', models.NullBooleanField(default=None, verbose_name='Status', db_index=True)),
                ('closed', models.BooleanField(default=False, db_index=True, verbose_name='Closed')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Updated')),
                ('source', models.ForeignKey(related_name='negotiations_made', verbose_name='Asker', to=settings.AUTH_USER_MODEL)),
                ('target', models.ForeignKey(related_name='negotiations_received', verbose_name='Target', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'negotiation',
                'verbose_name_plural': 'negotiations',
            },
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('group', models.OneToOneField(related_name='message_quota', primary_key=True, serialize=False, to='auth.Group', verbose_name='Group')),
                ('max_threads', models.SmallIntegerField(default=10, verbose_name='Max threads/day')),
            ],
            options={
                'verbose_name': 'message quota',
                'verbose_name_plural': 'message quotas',
                'permissions': (('unlimited_threads', 'Can overstep thread quotas'), ('unlimited_messages', 'Can overstep message quotas')),
            },
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('active', models.BooleanField(default=True, db_index=True, verbose_name='Is active')),
                ('unread', models.BooleanField(default=True, db_index=True, verbose_name='Unread')),
                ('unread_date', models.DateTimeField(default=None, null=True, verbose_name='Unread time')),
                ('counter', models.PositiveSmallIntegerField(default=0, verbose_name='Message count')),
                ('acknowledged', models.BooleanField(default=False, verbose_name='Acknowledged')),
            ],
            options={
                'verbose_name': 'recipient',
                'verbose_name_plural': 'recipients',
            },
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('topic', models.CharField(db_index=True, max_length=128, verbose_name='Topic', blank=True)),
                ('started', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Was started')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Updated', db_index=True)),
                ('deleted', models.BooleanField(default=False, db_index=True, verbose_name='Deleted')),
                ('counter', models.IntegerField(default=0, verbose_name='Message count')),
                ('population', models.IntegerField(default=0, verbose_name='Recipient count')),
                ('closed', models.BooleanField(default=False, db_index=True, verbose_name='Closed')),
                ('expires', models.DateTimeField(null=True, verbose_name='Expires', blank=True)),
                ('expiry_on_read', models.SmallIntegerField(default=365, help_text='Value in days', verbose_name='Expiry on read')),
                ('author', models.ForeignKey(related_name='threads', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Author', to=settings.AUTH_USER_MODEL, null=True)),
                ('labels', models.ManyToManyField(to='messaging.Label', verbose_name='Labels', blank=True)),
                ('updater', models.ForeignKey(related_name='threads_where_last', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Last speaker', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'thread',
                'verbose_name_plural': 'threads',
            },
        ),
        migrations.AddField(
            model_name='recipient',
            name='thread',
            field=models.ForeignKey(related_name='recipients', verbose_name='Thread', to='messaging.Thread'),
        ),
        migrations.AddField(
            model_name='recipient',
            name='user',
            field=models.ForeignKey(related_name='user_recipients', verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='negotiation',
            name='thread',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Thread', to='messaging.Thread', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(related_name='messages', verbose_name='Thread', to='messaging.Thread'),
        ),
        migrations.AddField(
            model_name='mailevent',
            name='type',
            field=models.ForeignKey(related_name='events', verbose_name='Mail type', to='messaging.MailType'),
        ),
        migrations.AlterUniqueTogether(
            name='recipient',
            unique_together=set([('thread', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='negotiation',
            unique_together=set([('source', 'target')]),
        ),
        migrations.AlterUniqueTogether(
            name='label',
            unique_together=set([('user', 'name')]),
        ),
    ]
