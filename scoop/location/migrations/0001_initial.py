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
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('position', django.contrib.gis.db.models.fields.PointField(default=(0.0, 0.0), srid=4326)),
                ('id', models.IntegerField(serialize=False, verbose_name='Geonames ID', primary_key=True)),
                ('city', models.BooleanField(default=False, db_index=True, verbose_name='City?')),
                ('type', models.CharField(max_length=8, verbose_name='Type')),
                ('feature', models.CharField(max_length=1, verbose_name='Feature')),
                ('a1', models.CharField(max_length=16, verbose_name='A1', blank=True)),
                ('a2', models.CharField(max_length=16, verbose_name='A2', blank=True)),
                ('a3', models.CharField(max_length=16, verbose_name='A3', blank=True)),
                ('a4', models.CharField(max_length=16, verbose_name='A4', blank=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('ascii', models.CharField(max_length=200, verbose_name='ASCII', db_index=True)),
                ('code', models.CharField(max_length=32, verbose_name='Code', blank=True)),
                ('population', models.IntegerField(default=0, verbose_name='Population', db_index=True)),
                ('level', models.SmallIntegerField(default=0, verbose_name='Level')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='CityName',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='Alternate ID', primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language name', blank=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('ascii', models.CharField(max_length=200, verbose_name='Name', db_index=True)),
                ('preferred', models.BooleanField(default=False, verbose_name='Preferred')),
                ('short', models.BooleanField(default=False, verbose_name='Short version')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'city name',
                'verbose_name_plural': 'city names',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('position', django.contrib.gis.db.models.fields.PointField(default=(0.0, 0.0), srid=4326)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('code2', models.CharField(unique=True, max_length=2, verbose_name='ISO Code', db_index=True)),
                ('code3', models.CharField(unique=True, max_length=3, verbose_name='ISO Code 3', db_index=True)),
                ('phone', models.CharField(default=b'', max_length=8, verbose_name='Phone prefix', blank=True)),
                ('continent', models.CharField(db_index=True, max_length=2, verbose_name='Continent', choices=[[b'AF', 'Africa'], [b'AS', 'Asia'], [b'EU', 'Europe'], [b'NA', 'North America'], [b'OC', 'Oceania'], [b'SA', 'South America'], [b'AN', 'Antarctica']])),
                ('population', models.IntegerField(default=0, verbose_name='Population')),
                ('area', models.FloatField(default=0, verbose_name='Area')),
                ('capital', models.CharField(max_length=96, verbose_name='Capital', blank=True)),
                ('regional_level', models.SmallIntegerField(default=1, verbose_name='Regional level')),
                ('subregional_level', models.SmallIntegerField(default=2, verbose_name='Sub-regional level')),
                ('public', models.BooleanField(default=False, db_index=True, verbose_name='Public')),
                ('safe', models.BooleanField(default=False, verbose_name='Safe')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Last update')),
            ],
            options={
                'verbose_name': 'country',
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='CountryName',
            fields=[
                ('id', models.IntegerField(serialize=False, verbose_name='Alternate ID', primary_key=True)),
                ('language', models.CharField(max_length=10, verbose_name='Language name')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('preferred', models.BooleanField(default=False, verbose_name='Preferred')),
                ('short', models.BooleanField(default=False, verbose_name='Short version')),
            ],
            options={
                'verbose_name': 'country name',
                'verbose_name_plural': 'country names',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('short_name', models.CharField(unique=True, max_length=6, verbose_name='3 letter name')),
                ('balance', models.DecimalField(default=-1, verbose_name='Quote', max_digits=10, decimal_places=7)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
            ],
            options={
                'verbose_name': 'currency',
                'verbose_name_plural': 'currencies',
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('position', django.contrib.gis.db.models.fields.PointField(default=(0.0, 0.0), srid=4326)),
            ],
            options={
                'verbose_name': 'user position',
                'verbose_name_plural': 'user positioning',
            },
        ),
        migrations.CreateModel(
            name='Timezone',
            fields=[
                ('name', models.CharField(unique=True, max_length=64, verbose_name='Name')),
                ('hash', models.IntegerField(help_text='Adler32 hash of timezone standard name', verbose_name='Name hash', serialize=False, editable=False, primary_key=True)),
            ],
            options={
                'verbose_name': 'timezone',
                'verbose_name_plural': 'timezones',
            },
        ),
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('position', django.contrib.gis.db.models.fields.PointField(default=(0.0, 0.0), srid=4326)),
                ('name', models.CharField(max_length=64, verbose_name='Name', db_index=True)),
                ('street', models.CharField(help_text='Way number, type and name', max_length=80, verbose_name='Way', db_index=True)),
                ('full', models.CharField(help_text='Full address, lines separated by semicolons', max_length=250, verbose_name='Full address')),
                ('url', models.URLField(max_length=160, verbose_name='URL', blank=True)),
            ],
            options={
                'verbose_name': 'venue',
                'verbose_name_plural': 'venues',
            },
        ),
        migrations.CreateModel(
            name='VenueType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('short_name', models.CharField(max_length=32, verbose_name='Short name', db_index=True)),
                ('parent', models.ForeignKey(related_name='children', verbose_name='Parent', to='location.VenueType', null=True)),
            ],
            options={
                'verbose_name': 'venue type',
                'verbose_name_plural': 'venue types',
            },
        ),
        migrations.CreateModel(
            name='VenueTypeTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=15, verbose_name='language', choices=[(b'en', 'English'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=48, verbose_name='Name')),
                ('plural', models.CharField(default=b'__', max_length=48, verbose_name='Plural')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('model', models.ForeignKey(related_name='translations', verbose_name=b'venuetype', to='location.VenueType')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
    ]
