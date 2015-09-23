# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import easy_thumbnails.fields
from django.db import migrations, models

import scoop.core.abstract.core.icon
import scoop.core.abstract.core.translation
import scoop.core.abstract.core.uuid
import scoop.core.util.data.dateutil


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('object_id', models.PositiveIntegerField(blank=True, verbose_name='Object Id')),
            ],
            options={
                'verbose_name_plural': 'block configurations',
                'verbose_name': 'block configuration',
            },
        ),
        migrations.CreateModel(
            name='Excerpt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('name', models.CharField(unique=True, verbose_name='Name', max_length=48)),
                ('title', models.CharField(unique=True, verbose_name='Title', max_length=80)),
                ('visible', models.BooleanField(verbose_name='Visible', default=True)),
                ('format', models.SmallIntegerField(choices=[[0, 'Plain HTML'], [1, 'Markdown'], [2, 'Textile'], [3, 'reStructured Text']], verbose_name='Format', default=0)),
                ('description', models.TextField(blank=True, verbose_name='Description', default='')),
                ('libraries', models.CharField(help_text='{% load %} libraries, comma separated', verbose_name='Tag libs', max_length=40)),
            ],
            options={
                'verbose_name_plural': 'excerpts',
                'verbose_name': 'excerpt',
            },
        ),
        migrations.CreateModel(
            name='ExcerptTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], verbose_name='language', max_length=15)),
                ('text', models.TextField(verbose_name='Text')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('se_indexed', models.BooleanField(db_index=True, verbose_name='Index in search engines', default=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('name', models.CharField(unique=True, verbose_name='Name', max_length=64)),
                ('title', models.CharField(verbose_name='Title', max_length=64)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('keywords', models.CharField(blank=True, verbose_name='Keywords', max_length=160)),
                ('path', models.CharField(help_text='Page URL', verbose_name='Path', max_length=160)),
                ('active', models.BooleanField(verbose_name='Active', default=True)),
                ('heading', models.TextField(blank=True, verbose_name='Page header extra code')),
                ('anonymous', models.BooleanField(verbose_name='Anonymous access', default=True)),
                ('authenticated', models.BooleanField(verbose_name='Authenticated access', default=True)),
            ],
            options={
                'verbose_name_plural': 'pages',
                'verbose_name': 'page',
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field='icon_height', verbose_name='Icon', max_length=96, blank=True, upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, width_field='icon_width', help_text='Maximum size 64x64')),
                ('icon_width', models.IntegerField(blank=True, verbose_name='Width', null=True, editable=False)),
                ('icon_height', models.IntegerField(blank=True, verbose_name='Height', null=True, editable=False)),
                ('name', models.SlugField(unique=True, verbose_name='Name', help_text='Name used for the position block in a template', max_length=64)),
                ('title', models.CharField(verbose_name='Title', max_length=64)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('anonymous', models.BooleanField(verbose_name='Anonymous access', default=True)),
                ('authenticated', models.BooleanField(verbose_name='Authenticated access', default=True)),
                ('groups', models.ManyToManyField(blank=True, verbose_name='Access for groups', to='auth.Group')),
            ],
            options={
                'verbose_name_plural': 'positions',
                'verbose_name': 'position',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('name', models.CharField(unique=True, verbose_name='Name', max_length=32)),
                ('path', models.CharField(unique=True, verbose_name='Path', max_length=64)),
                ('full', models.BooleanField(verbose_name='Full page template', default=False, help_text='Contains html, head and body tags.')),
                ('positions', models.ManyToManyField(blank=True, verbose_name='Positions', to='editorial.Position')),
            ],
            options={
                'verbose_name_plural': 'templates',
                'verbose_name': 'template',
            },
        ),
    ]
