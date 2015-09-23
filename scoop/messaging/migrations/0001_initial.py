# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
import django.utils.timezone
import picklefield.fields
from django.db import migrations, models

import scoop.core.abstract.core.translation
import scoop.core.abstract.core.uuid
import scoop.core.util.data.dateutil


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('level', models.SmallIntegerField(choices=[[0, 'Warning'], [1, 'Important'], [2, 'Security']], verbose_name='Level', default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(2)])),
                ('title', models.CharField(verbose_name='Title', max_length=80)),
                ('text', models.TextField(verbose_name='Text')),
                ('items', models.CharField(verbose_name='Items', default='', max_length=128)),
                ('read', models.BooleanField(db_index=True, verbose_name='Read', default=False)),
                ('read_time', models.DateTimeField(db_index=True, verbose_name='Read', default=None, null=True)),
            ],
            options={
                'verbose_name_plural': 'alerts',
                'verbose_name': 'alert',
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('name', models.CharField(validators=[django.core.validators.RegexValidator('^[\\d\\w][\\d\\s\\w]*$', 'Must contain only letters and digits')], db_index=True, verbose_name='Name', max_length=40)),
            ],
            options={
                'verbose_name_plural': 'labels',
                'verbose_name': 'label',
            },
        ),
        migrations.CreateModel(
            name='MailEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=128, unique=True, max_length=22, default='', editable=False)),
                ('queued', models.DateTimeField(verbose_name='Queue time', default=django.utils.timezone.now)),
                ('forced', models.BooleanField(db_index=True, verbose_name='Force sending', default=False)),
                ('sent', models.BooleanField(db_index=True, verbose_name='Sent', default=False)),
                ('sent_time', models.DateTimeField(verbose_name='Delivery time', default=None, null=True)),
                ('sent_email', models.CharField(verbose_name='Email used', default='', max_length=96)),
                ('minimum_time', models.DateTimeField(verbose_name='Minimum delivery', default=django.utils.timezone.now)),
                ('discarded', models.BooleanField(verbose_name='Discarded', default=False)),
            ],
            options={
                'verbose_name_plural': 'mail events',
                'verbose_name': 'mail event',
            },
        ),
        migrations.CreateModel(
            name='MailType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('short_name', models.CharField(verbose_name='Codename', max_length=32)),
                ('template', models.CharField(help_text='Template filename without path and extension', verbose_name='Template', max_length=32)),
                ('interval', models.IntegerField(choices=[[0, 'As soon as possible'], [5, 'Every 5 minutes'], [10, 'Every 10 minutes'], [30, 'Every 30 minutes'], [60, 'Every hour'], [720, 'Every 12 hours'], [1440, 'Every day'], [4320, 'Every 3 days'], [10080, 'Every week'], [43200, 'Every 30 days']], verbose_name='Minimum delay', default=0, help_text='Delay in minutes')),
            ],
            options={
                'verbose_name_plural': 'mail types',
                'verbose_name': 'mail type',
            },
        ),
        migrations.CreateModel(
            name='MailTypeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], verbose_name='language', max_length=15)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('name', models.CharField(verbose_name='Name', max_length=32)),
                ('text', models.TextField(verbose_name='Text')),
                ('spam', models.FloatField(verbose_name='Spam level', default=0.0, validators=[django.core.validators.MaxValueValidator(1.0), django.core.validators.MinValueValidator(0.0)])),
                ('deleted', models.BooleanField(db_index=True, verbose_name='Deleted', default=False)),
            ],
            options={
                'verbose_name_plural': 'messages',
                'verbose_name': 'message',
                'permissions': (('can_force_send', 'Can force send messages'), ('can_broadcast', 'Can broadcast messages')),
            },
        ),
        migrations.CreateModel(
            name='Negotiation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('status', models.NullBooleanField(db_index=True, verbose_name='Status', default=None)),
                ('closed', models.BooleanField(db_index=True, verbose_name='Closed', default=False)),
                ('updated', models.DateTimeField(verbose_name='Updated', default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name_plural': 'negotiations',
                'verbose_name': 'negotiation',
            },
        ),
        migrations.CreateModel(
            name='Quota',
            fields=[
                ('group', models.OneToOneField(primary_key=True, verbose_name='Group', to='auth.Group', related_name='message_quota', serialize=False)),
                ('max_threads', models.SmallIntegerField(verbose_name='Max threads/day', default=10)),
            ],
            options={
                'verbose_name_plural': 'message quotas',
                'verbose_name': 'message quota',
                'permissions': (('unlimited_threads', 'Can overstep thread quotas'), ('unlimited_messages', 'Can overstep message quotas')),
            },
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('active', models.BooleanField(db_index=True, verbose_name='Is active', default=True)),
                ('unread', models.BooleanField(db_index=True, verbose_name='Unread', default=True)),
                ('unread_date', models.DateTimeField(verbose_name='Unread time', default=None, null=True)),
                ('counter', models.PositiveSmallIntegerField(verbose_name='Message count', default=0)),
                ('acknowledged', models.BooleanField(verbose_name='Acknowledged', default=False)),
            ],
            options={
                'verbose_name_plural': 'recipients',
                'verbose_name': 'recipient',
            },
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('topic', models.CharField(blank=True, db_index=True, verbose_name='Topic', max_length=128)),
                ('started', models.DateTimeField(verbose_name='Was started', default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(db_index=True, verbose_name='Updated', default=django.utils.timezone.now)),
                ('deleted', models.BooleanField(db_index=True, verbose_name='Deleted', default=False)),
                ('counter', models.IntegerField(verbose_name='Message count', default=0)),
                ('population', models.IntegerField(verbose_name='Recipient count', default=0)),
                ('closed', models.BooleanField(db_index=True, verbose_name='Closed', default=False)),
                ('expires', models.DateTimeField(blank=True, verbose_name='Expires', null=True)),
                ('expiry_on_read', models.SmallIntegerField(verbose_name='Expiry on read', default=365, help_text='Value in days')),
            ],
            options={
                'verbose_name_plural': 'threads',
                'verbose_name': 'thread',
            },
        ),
    ]
