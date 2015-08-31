# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import scoop.core.abstract.core.icon
import scoop.core.abstract.core.uuid
import scoop.forum.models.sanction
import scoop.core.util.data.dateutil
import picklefield.fields
import autoslug.fields
import scoop.core.util.model.fields
import scoop.forum.util.read
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field=b'icon_height', width_field=b'icon_width', upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, max_length=96, blank=True, help_text='Taille maximum 64x64', verbose_name='Icon')),
                ('icon_width', models.IntegerField(verbose_name='Width', null=True, editable=False, blank=True)),
                ('icon_height', models.IntegerField(verbose_name='Height', null=True, editable=False, blank=True)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('access_level', models.SmallIntegerField(default=0, db_index=True, verbose_name='Access level', choices=[[0, 'Public'], [1, 'Members only'], [2, 'Staff only']])),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('locked', models.BooleanField(default=False, help_text='Protected from the creation of new topics', verbose_name='Locked')),
                ('visible', models.BooleanField(default=True, verbose_name='Visible')),
                ('slug', autoslug.fields.AutoSlugField(max_length=100, blank=True)),
                ('topic_count', models.IntegerField(default=0, verbose_name='Topics count')),
                ('post_count', models.IntegerField(default=0, verbose_name='Posts count')),
                ('root', models.BooleanField(default=False, help_text='Appears on the forum index', verbose_name='Root')),
            ],
            options={
                'verbose_name': 'forum',
                'verbose_name_plural': 'forums',
            },
        ),
        migrations.CreateModel(
            name='IgnoreList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
            ],
            options={
                'verbose_name': 'ignore list',
                'verbose_name_plural': 'ignore lists',
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=128, unique=True, max_length=22, editable=False)),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('title', models.CharField(max_length=192, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('published', models.BooleanField(default=True, db_index=True, verbose_name='Published')),
                ('expires', models.DateTimeField(null=True, verbose_name='Expires', blank=True)),
                ('answers', scoop.core.util.model.fields.LineListField(default=b'Yes\nNo', help_text='Enter one answer per line', verbose_name='Answers')),
                ('slug', autoslug.fields.AutoSlugField(max_length=100, editable=False, blank=True)),
                ('closed', models.BooleanField(default=False, db_index=True, verbose_name='Closed')),
            ],
            options={
                'verbose_name': 'poll',
                'verbose_name_plural': 'polls',
            },
        ),
        migrations.CreateModel(
            name='Read',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expiry', models.DateTimeField(default=scoop.forum.util.read.default_expiry, null=True, verbose_name='Expiry')),
                ('created', models.DateTimeField(auto_now=True, verbose_name='Created')),
            ],
            options={
                'verbose_name': 'topic read',
                'verbose_name_plural': 'topics read',
            },
        ),
        migrations.CreateModel(
            name='Sanction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('type', models.SmallIntegerField(default=0, db_index=True, verbose_name='Type', choices=[[0, 'Posting disabled'], [1, 'Reading disabled']])),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('expires', models.DateTimeField(default=scoop.forum.models.sanction.get_default_expiry, verbose_name='Expiry')),
                ('revoked', models.BooleanField(default=False, verbose_name='Revoked')),
            ],
            options={
                'verbose_name': 'sanction',
                'verbose_name_plural': 'sanctions',
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('choice', models.SmallIntegerField(default=None, null=True, verbose_name='Choice')),
            ],
            options={
                'verbose_name': 'vote',
                'verbose_name_plural': 'votes',
            },
        ),
    ]
