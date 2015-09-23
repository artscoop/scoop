# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import autoslug.fields
import easy_thumbnails.fields
import picklefield.fields
from django.db import migrations, models

import scoop.core.abstract.core.icon
import scoop.core.abstract.core.uuid
import scoop.core.util.data.dateutil
import scoop.core.util.model.fields
import scoop.forum.models.sanction
import scoop.forum.util.read


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field='icon_height', verbose_name='Icon', max_length=96, blank=True, upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, width_field='icon_width', help_text='Maximum size 64x64')),
                ('icon_width', models.IntegerField(blank=True, verbose_name='Width', null=True, editable=False)),
                ('icon_height', models.IntegerField(blank=True, verbose_name='Height', null=True, editable=False)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('access_level', models.SmallIntegerField(choices=[[0, 'Public'], [1, 'Members only'], [2, 'Staff only']], db_index=True, verbose_name='Access level', default=0)),
                ('name', models.CharField(verbose_name='Name', max_length=80)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('locked', models.BooleanField(verbose_name='Locked', default=False, help_text='Protected from the creation of new topics')),
                ('visible', models.BooleanField(verbose_name='Visible', default=True)),
                ('slug', autoslug.fields.AutoSlugField(populate_from='name', blank=True, unique_with=('id',), editable=True)),
                ('topic_count', models.IntegerField(verbose_name='Topics count', default=0)),
                ('post_count', models.IntegerField(verbose_name='Posts count', default=0)),
                ('root', models.BooleanField(verbose_name='Root', default=False, help_text='Appears on the forum index')),
            ],
            options={
                'verbose_name_plural': 'forums',
                'verbose_name': 'forum',
            },
        ),
        migrations.CreateModel(
            name='IgnoreList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
            ],
            options={
                'verbose_name_plural': 'ignore lists',
                'verbose_name': 'ignore list',
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=128, unique=True, max_length=22, default='', editable=False)),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('title', models.CharField(verbose_name='Title', max_length=192)),
                ('description', models.TextField(verbose_name='Description')),
                ('published', models.BooleanField(db_index=True, verbose_name='Published', default=True)),
                ('expires', models.DateTimeField(blank=True, verbose_name='Expires', null=True)),
                ('answers', scoop.core.util.model.fields.LineListField(verbose_name='Answers', default='Yes\nNo', help_text='Enter one answer per line')),
                ('slug', autoslug.fields.AutoSlugField(blank=True, populate_from='title', unique_with=('id',), editable=False)),
                ('closed', models.BooleanField(db_index=True, verbose_name='Closed', default=False)),
            ],
            options={
                'verbose_name_plural': 'polls',
                'verbose_name': 'poll',
            },
        ),
        migrations.CreateModel(
            name='Read',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('expiry', models.DateTimeField(verbose_name='Expiry', default=scoop.forum.util.read.default_expiry, null=True)),
                ('created', models.DateTimeField(verbose_name='Created', auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'topics read',
                'verbose_name': 'topic read',
            },
        ),
        migrations.CreateModel(
            name='Sanction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('type', models.SmallIntegerField(choices=[[0, 'Posting disabled'], [1, 'Reading disabled']], db_index=True, verbose_name='Type', default=0)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('expires', models.DateTimeField(verbose_name='Expiry', default=scoop.forum.models.sanction.get_default_expiry)),
                ('revoked', models.BooleanField(verbose_name='Revoked', default=False)),
            ],
            options={
                'verbose_name_plural': 'sanctions',
                'verbose_name': 'sanction',
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('choice', models.SmallIntegerField(verbose_name='Choice', default=None, null=True)),
            ],
            options={
                'verbose_name_plural': 'votes',
                'verbose_name': 'vote',
            },
        ),
    ]
