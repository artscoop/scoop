# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import annoying.fields
import django.core.validators
import django.utils.timezone
import picklefield.fields
from django.conf import settings
from django.db import migrations, models

import scoop.core.abstract.core.uuid
import scoop.core.util.data.dateutil
import scoop.user.models.user


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('username', models.CharField(unique=True, max_length=32, verbose_name='Username', validators=[django.core.validators.RegexValidator(regex=b'^[A-Za-z0-9][A-Za-z0-9_]+', message='Your name must start with a letter and can only contain letters, digits and underscores'), django.core.validators.MinLengthValidator(4)])),
                ('name', models.CharField(blank=True, max_length=24, verbose_name='Name', validators=[django.core.validators.RegexValidator(regex=b'^[A-Za-z][A-Za-z0-9_\\-]+$', message='Your name can only contain letters')])),
                ('bot', models.BooleanField(default=False, verbose_name='Bot')),
                ('email', models.EmailField(unique=True, max_length=96, verbose_name='Email', blank=True)),
                ('is_active', models.BooleanField(default=True, db_index=True, verbose_name='Active')),
                ('deleted', models.BooleanField(default=False, db_index=True, verbose_name='Deleted')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='Staff')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date joined')),
                ('last_online', models.DateTimeField(default=None, null=True, verbose_name='Last online', db_index=True)),
                ('next_mail', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Next possible mail for user', editable=False)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', scoop.user.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='FormConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('name', models.CharField(max_length=32, verbose_name='Form name')),
                ('version', models.CharField(help_text='Variation name', max_length=24, verbose_name='Version', blank=True)),
                ('data', picklefield.fields.PickledObjectField(default={}, verbose_name='Data', editable=False)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'verbose_name': 'user configuration',
                'verbose_name_plural': 'user configurations',
            },
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
            ],
            options={
                'verbose_name': 'profile visit',
                'verbose_name_plural': 'profile visits',
                'permissions': (('can_ghost_visit', 'Can visit stealth'),),
            },
        ),
        migrations.CreateModel(
            name='Activation',
            fields=[
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=128, unique=True, max_length=22, editable=False)),
                ('user', annoying.fields.AutoOneToOneField(related_name='activation', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('question', models.IntegerField(null=True, verbose_name='Secret question')),
                ('answer', models.CharField(max_length=48, verbose_name='Answer', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('updates', models.SmallIntegerField(default=0, verbose_name='Updates')),
                ('resends', models.SmallIntegerField(default=0, verbose_name='Mail send count')),
                ('details', models.CharField(default=b'', max_length=48, verbose_name='Admin details', blank=True)),
            ],
            options={
                'verbose_name': 'user activation',
                'verbose_name_plural': 'user activations',
            },
        ),
        migrations.AddField(
            model_name='visit',
            name='user',
            field=models.ForeignKey(related_name='visits_receiver', verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='visit',
            name='visitor',
            field=models.ForeignKey(related_name='visits_maker', verbose_name='Visitor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='formconfiguration',
            name='user',
            field=models.ForeignKey(related_name='configurations', verbose_name='User', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='visit',
            unique_together=set([('visitor', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='formconfiguration',
            unique_together=set([('user', 'name', 'version')]),
        ),
    ]
