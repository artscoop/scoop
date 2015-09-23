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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('username', models.CharField(unique=True, validators=[django.core.validators.RegexValidator(message='Your name must start with a letter and can only contain letters, digits and underscores', regex='^[A-Za-z0-9][A-Za-z0-9_]+$'), django.core.validators.MinLengthValidator(4)], verbose_name='Username', max_length=32)),
                ('name', models.CharField(blank=True, validators=[django.core.validators.RegexValidator(message='Your name can only contain letters', regex='^[A-Za-z][A-Za-z0-9_\\-]+$')], verbose_name='Name', max_length=24)),
                ('bot', models.BooleanField(verbose_name='Bot', default=False)),
                ('email', models.EmailField(unique=True, blank=True, verbose_name='Email', max_length=96)),
                ('is_active', models.BooleanField(db_index=True, verbose_name='Active', default=True)),
                ('deleted', models.BooleanField(db_index=True, verbose_name='Deleted', default=False)),
                ('is_staff', models.BooleanField(verbose_name='Staff', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('date_joined', models.DateTimeField(verbose_name='Date joined', default=django.utils.timezone.now)),
                ('last_online', models.DateTimeField(db_index=True, verbose_name='Last online', default=None, null=True)),
                ('next_mail', models.DateTimeField(verbose_name='Next possible mail for user', default=django.utils.timezone.now, editable=False)),
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
            },
            managers=[
                ('objects', scoop.user.models.user.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='FormConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('name', models.CharField(verbose_name='Form name', max_length=32)),
                ('version', models.CharField(blank=True, help_text='Variation name', verbose_name='Version', max_length=24)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default={}, editable=False)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name_plural': 'user configurations',
                'verbose_name': 'user configuration',
            },
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
            ],
            options={
                'verbose_name_plural': 'profile visits',
                'verbose_name': 'profile visit',
                'permissions': (('can_ghost_visit', 'Can visit stealth'),),
            },
        ),
        migrations.CreateModel(
            name='Activation',
            fields=[
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=128, unique=True, max_length=22, default='', editable=False)),
                ('user', annoying.fields.AutoOneToOneField(primary_key=True, verbose_name='User', to=settings.AUTH_USER_MODEL, related_name='activation', serialize=False)),
                ('question', models.IntegerField(verbose_name='Secret question', null=True)),
                ('answer', models.CharField(blank=True, verbose_name='Answer', max_length=48)),
                ('active', models.BooleanField(verbose_name='Active', default=True)),
                ('updates', models.SmallIntegerField(verbose_name='Updates', default=0)),
                ('resends', models.SmallIntegerField(verbose_name='Mail send count', default=0)),
                ('details', models.CharField(blank=True, verbose_name='Admin details', default='', max_length=48)),
            ],
            options={
                'verbose_name_plural': 'user activations',
                'verbose_name': 'user activation',
            },
        ),
        migrations.AddField(
            model_name='visit',
            name='user',
            field=models.ForeignKey(related_name='visits_receiver', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='visit',
            name='visitor',
            field=models.ForeignKey(related_name='visits_maker', to=settings.AUTH_USER_MODEL, verbose_name='Visitor'),
        ),
        migrations.AddField(
            model_name='formconfiguration',
            name='user',
            field=models.ForeignKey(related_name='configurations', to=settings.AUTH_USER_MODEL, null=True, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_name='user_set', to='auth.Group', verbose_name='groups', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_name='user_set', to='auth.Permission', verbose_name='user permissions', blank=True, help_text='Specific permissions for this user.', related_query_name='user'),
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
