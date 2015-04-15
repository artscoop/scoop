# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import easy_thumbnails.fields
from django.conf import settings
from django.db import migrations, models

import scoop.core.util.data.dateutil


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('object_id', models.PositiveIntegerField(verbose_name='Object Id', blank=True)),
                ('content_type', models.ForeignKey(verbose_name='Content type', to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'block configuration',
                'verbose_name_plural': 'block configurations',
            },
        ),
        migrations.CreateModel(
            name='Excerpt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('name', models.CharField(unique=True, max_length=48, verbose_name='Name')),
                ('title', models.CharField(unique=True, max_length=80, verbose_name='Title')),
                ('visible', models.BooleanField(default=True, verbose_name='Visible')),
                ('format', models.SmallIntegerField(default=0, verbose_name='Format', choices=[[0, 'Plain HTML'], [1, 'Markdown'], [2, 'Textile'], [3, 'reStructured Text']])),
                ('description', models.TextField(default='', verbose_name='Description', blank=True)),
                ('libraries', models.CharField(help_text='{% load %} libraries, comma separated', max_length=40, verbose_name='Tag libs')),
                ('author', models.ForeignKey(verbose_name='Author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'excerpt',
                'verbose_name_plural': 'excerpts',
            },
        ),
        migrations.CreateModel(
            name='ExcerptTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=15, verbose_name='language', choices=[(b'en', 'English'), (b'fr', 'French')])),
                ('text', models.TextField(verbose_name='Text')),
                ('model', models.ForeignKey(related_name='translations', verbose_name=b'excerpt', to='scoop.editorial.Excerpt')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('se_indexed', models.BooleanField(default=False, db_index=True, verbose_name='Index in search engines')),
                ('name', models.CharField(unique=True, max_length=64, verbose_name='Name')),
                ('title', models.CharField(max_length=64, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('keywords', models.CharField(max_length=160, verbose_name='Keywords', blank=True)),
                ('path', models.CharField(help_text='Page URL', max_length=160, verbose_name='Path')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('heading', models.TextField(verbose_name='Page header extra code', blank=True)),
                ('anonymous', models.BooleanField(default=True, verbose_name='Anonymous access')),
                ('authenticated', models.BooleanField(default=True, verbose_name='Authenticated access')),
                ('author', models.ForeignKey(verbose_name='Author', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='scoop.editorial.Page', help_text='Parent page, used in lists and breadcrumbs', null=True, verbose_name='Parent')),
            ],
            options={
                'verbose_name': 'page',
                'verbose_name_plural': 'pages',
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field=b'icon_height', width_field=b'icon_width', upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, max_length=96, blank=True, help_text='Taille maximum 64x64', verbose_name='Icon')),
                ('icon_width', models.IntegerField(verbose_name='Width', null=True, editable=False, blank=True)),
                ('icon_height', models.IntegerField(verbose_name='Height', null=True, editable=False, blank=True)),
                ('name', models.SlugField(help_text='Name used for the position block in a template', unique=True, max_length=64, verbose_name='Name')),
                ('title', models.CharField(max_length=64, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('anonymous', models.BooleanField(default=True, verbose_name='Anonymous access')),
                ('authenticated', models.BooleanField(default=True, verbose_name='Authenticated access')),
                ('groups', models.ManyToManyField(to='auth.Group', verbose_name='Access for groups', blank=True)),
            ],
            options={
                'verbose_name': 'position',
                'verbose_name_plural': 'positions',
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('name', models.CharField(unique=True, max_length=32, verbose_name='Name')),
                ('path', models.CharField(unique=True, max_length=64, verbose_name='Path')),
                ('full', models.BooleanField(default=False, help_text='Contains html, head and body tags.', verbose_name='Full page template')),
                ('positions', models.ManyToManyField(to='scoop.editorial.Position', verbose_name='Positions', blank=True)),
            ],
            options={
                'verbose_name': 'template',
                'verbose_name_plural': 'templates',
            },
        ),
        migrations.AddField(
            model_name='page',
            name='template',
            field=models.ForeignKey(related_name='pages', verbose_name='Template', to='scoop.editorial.Template'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='page',
            field=models.ForeignKey(related_name='configurations', verbose_name='Page', to='scoop.editorial.Page'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='position',
            field=models.ForeignKey(related_name='configurations', verbose_name='Position', to='scoop.editorial.Position'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='template',
            field=models.ForeignKey(related_name='configurations', verbose_name='Template', to='scoop.editorial.Template'),
        ),
        migrations.AlterUniqueTogether(
            name='configuration',
            unique_together=set([('page', 'position', 'template', 'content_type', 'object_id')]),
        ),
    ]
