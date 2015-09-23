# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
import django.utils.timezone
import picklefield.fields
from django.db import migrations, models

import scoop.core.abstract.core.translation
import scoop.core.util.data.dateutil


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=4326, default=(0.0, 0.0))),
                ('id', models.IntegerField(primary_key=True, verbose_name='Geonames ID', serialize=False)),
                ('city', models.BooleanField(db_index=True, verbose_name='City?', default=False)),
                ('type', models.CharField(verbose_name='Type', max_length=8)),
                ('feature', models.CharField(verbose_name='Feature', max_length=1)),
                ('a1', models.CharField(blank=True, verbose_name='A1', max_length=16)),
                ('a2', models.CharField(blank=True, verbose_name='A2', max_length=16)),
                ('a3', models.CharField(blank=True, verbose_name='A3', max_length=16)),
                ('a4', models.CharField(blank=True, verbose_name='A4', max_length=16)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('ascii', models.CharField(db_index=True, verbose_name='ASCII', max_length=200)),
                ('code', models.CharField(blank=True, verbose_name='Code', max_length=32)),
                ('population', models.IntegerField(db_index=True, verbose_name='Population', default=0)),
                ('level', models.SmallIntegerField(verbose_name='Level', default=0)),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'cities',
                'verbose_name': 'city',
            },
        ),
        migrations.CreateModel(
            name='CityName',
            fields=[
                ('id', models.IntegerField(primary_key=True, verbose_name='Alternate ID', serialize=False)),
                ('language', models.CharField(blank=True, verbose_name='Language name', max_length=10)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('ascii', models.CharField(db_index=True, verbose_name='Name', max_length=200)),
                ('preferred', models.BooleanField(verbose_name='Preferred', default=False)),
                ('short', models.BooleanField(verbose_name='Short version', default=False)),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'city names',
                'verbose_name': 'city name',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=4326, default=(0.0, 0.0))),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
                ('code2', models.CharField(unique=True, db_index=True, verbose_name='ISO Code', max_length=2)),
                ('code3', models.CharField(unique=True, db_index=True, verbose_name='ISO Code 3', max_length=3)),
                ('phone', models.CharField(blank=True, verbose_name='Phone prefix', default='', max_length=8)),
                ('continent', models.CharField(choices=[['AF', 'Africa'], ['AS', 'Asia'], ['EU', 'Europe'], ['NA', 'North America'], ['OC', 'Oceania'], ['SA', 'South America'], ['AN', 'Antarctica']], db_index=True, verbose_name='Continent', max_length=2)),
                ('population', models.IntegerField(verbose_name='Population', default=0)),
                ('area', models.FloatField(verbose_name='Area', default=0)),
                ('capital', models.CharField(blank=True, verbose_name='Capital', max_length=96)),
                ('regional_level', models.SmallIntegerField(verbose_name='Regional level', default=1)),
                ('subregional_level', models.SmallIntegerField(verbose_name='Sub-regional level', default=2)),
                ('public', models.BooleanField(db_index=True, verbose_name='Public', default=False)),
                ('safe', models.BooleanField(verbose_name='Safe', default=False)),
                ('updated', models.DateTimeField(verbose_name='Last update', default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name_plural': 'countries',
                'verbose_name': 'country',
            },
        ),
        migrations.CreateModel(
            name='CountryName',
            fields=[
                ('id', models.IntegerField(primary_key=True, verbose_name='Alternate ID', serialize=False)),
                ('language', models.CharField(verbose_name='Language name', max_length=10)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('preferred', models.BooleanField(verbose_name='Preferred', default=False)),
                ('short', models.BooleanField(verbose_name='Short version', default=False)),
            ],
            options={
                'verbose_name_plural': 'country names',
                'verbose_name': 'country name',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=32)),
                ('short_name', models.CharField(unique=True, verbose_name='3 letter name', max_length=6)),
                ('balance', models.DecimalField(decimal_places=7, verbose_name='Quote', default=-1, max_digits=10)),
                ('updated', models.DateTimeField(verbose_name='Updated', auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'currencies',
                'verbose_name': 'currency',
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=4326, default=(0.0, 0.0))),
            ],
            options={
                'verbose_name_plural': 'user positioning',
                'verbose_name': 'user position',
            },
        ),
        migrations.CreateModel(
            name='Timezone',
            fields=[
                ('name', models.CharField(unique=True, verbose_name='Name', max_length=64)),
                ('code', models.BigIntegerField(primary_key=True, help_text='Adler32 hash of timezone standard name', verbose_name='Name hash', serialize=False, editable=True)),
            ],
            options={
                'verbose_name_plural': 'timezones',
                'verbose_name': 'timezone',
            },
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=4326, default=(0.0, 0.0))),
                ('name', models.CharField(db_index=True, verbose_name='Name', max_length=64)),
                ('street', models.CharField(help_text='Way number, type and name', db_index=True, verbose_name='Way', max_length=80)),
                ('full', models.CharField(help_text='Full address, lines separated by semicolons', verbose_name='Full address', max_length=250)),
                ('url', models.URLField(blank=True, verbose_name='URL', max_length=160)),
            ],
            options={
                'verbose_name_plural': 'venues',
                'verbose_name': 'venue',
            },
        ),
        migrations.CreateModel(
            name='VenueType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('short_name', models.CharField(db_index=True, verbose_name='Short name', max_length=32)),
                ('parent', models.ForeignKey(related_name='children', to='location.VenueType', null=True, verbose_name='Parent')),
            ],
            options={
                'verbose_name_plural': 'venue types',
                'verbose_name': 'venue type',
            },
        ),
        migrations.CreateModel(
            name='VenueTypeTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], verbose_name='language', max_length=15)),
                ('name', models.CharField(verbose_name='Name', max_length=48)),
                ('plural', models.CharField(verbose_name='Plural', default='__', max_length=48)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('model', models.ForeignKey(related_name='translations', to='location.VenueType', verbose_name='venuetype')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
    ]
