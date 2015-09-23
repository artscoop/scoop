# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import autoslug.fields
import django.utils.timezone
import easy_thumbnails.fields
import picklefield.fields
from django.db import migrations, models

import scoop.content.util.attachment
import scoop.content.util.picture
import scoop.core.abstract.core.generic
import scoop.core.abstract.core.icon
import scoop.core.abstract.core.rectangle
import scoop.core.abstract.core.translation
import scoop.core.abstract.core.uuid
import scoop.core.util.data.dateutil
import scoop.core.util.model.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field='icon_height', verbose_name='Icon', max_length=96, blank=True, upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, width_field='icon_width', help_text='Maximum size 64x64')),
                ('icon_width', models.IntegerField(blank=True, verbose_name='Width', null=True, editable=False)),
                ('icon_height', models.IntegerField(blank=True, verbose_name='Height', null=True, editable=False)),
                ('width', models.IntegerField(blank=True, verbose_name='Width', default=0, null=True)),
                ('height', models.IntegerField(blank=True, verbose_name='Height', default=0, null=True)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('name', models.CharField(unique=True, verbose_name='Name', max_length=32)),
                ('active', models.BooleanField(verbose_name='Active', default=True)),
                ('group', models.CharField(blank=True, help_text='Pipe separated', verbose_name='Group name', max_length=48)),
                ('code', models.TextField(verbose_name='HTML/JS Snippet', help_text='Django template code for HTML/JS')),
                ('views', models.IntegerField(verbose_name='Views', default=0, editable=False)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('network', models.CharField(choices=[['gg', 'Google Adsense'], ['af', 'AdFever'], ['na', 'Custom'], ['ot', 'Other']], db_index=True, verbose_name='Ad network', default='na', max_length=4)),
            ],
            options={
                'verbose_name_plural': 'advertisements',
                'verbose_name': 'advertisement',
            },
            bases=(models.Model, scoop.core.abstract.core.rectangle.RectangleObject),
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('object_id', models.PositiveIntegerField(blank=True, db_index=True, verbose_name='Object Id', null=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('access', models.SmallIntegerField(choices=[[0, 'Public'], [1, 'Friends'], [2, 'Personal'], [3, 'Friend groups'], [4, 'Registered users']], db_index=True, verbose_name='Access', default=0)),
                ('name', models.CharField(verbose_name='Name', max_length=96)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('updated', models.DateTimeField(verbose_name='Updated', auto_now=True)),
                ('visible', models.BooleanField(verbose_name='Visible', default=True)),
            ],
            options={
                'verbose_name_plural': 'picture albums',
                'verbose_name': 'picture album',
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.CreateModel(
            name='Animation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=128, unique=True, max_length=22, default='', editable=False)),
                ('file', models.FileField(upload_to=scoop.content.util.picture.get_animation_upload_path, verbose_name='File', max_length=192)),
                ('extension', models.CharField(verbose_name='Extension', default='mp4', max_length=8)),
                ('duration', models.FloatField(help_text='In seconds', db_index=True, verbose_name='Duration', default=0.0, editable=False)),
                ('title', models.CharField(blank=True, verbose_name='Title', max_length=96)),
                ('description', models.TextField(blank=True, verbose_name='Description', help_text='Description text. Enter an URL here to download a picture')),
                ('autoplay', models.BooleanField(verbose_name='Auto play', default=False)),
                ('loop', models.BooleanField(verbose_name='Loop', default=True)),
                ('deleted', models.BooleanField(verbose_name='Deleted', default=False)),
                ('updated', models.DateTimeField(verbose_name='Updated', auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Animations',
                'verbose_name': 'Animation',
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('group', models.CharField(blank=True, db_index=True, verbose_name='Group', max_length=16)),
                ('file', models.FileField(upload_to=scoop.content.util.attachment.get_attachment_upload_path, help_text='File to attach', verbose_name='File', max_length=192)),
                ('name', models.CharField(blank=True, verbose_name='Name', max_length=64)),
                ('description', models.TextField(blank=True, verbose_name='Description', default='')),
                ('mimetype', models.CharField(blank=True, verbose_name='MIME type', max_length=40)),
                ('object_id', models.PositiveIntegerField(blank=True, db_index=True, verbose_name='Object Id', null=True)),
            ],
            options={
                'verbose_name_plural': 'attachments',
                'verbose_name': 'attachment',
                'permissions': (('can_join_files', 'Can join files'),),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field='icon_height', verbose_name='Icon', max_length=96, blank=True, upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, width_field='icon_width', help_text='Maximum size 64x64')),
                ('icon_width', models.IntegerField(blank=True, verbose_name='Width', null=True, editable=False)),
                ('icon_height', models.IntegerField(blank=True, verbose_name='Height', null=True, editable=False)),
                ('short_name', models.CharField(verbose_name='Identifier', max_length=10)),
                ('url', models.CharField(help_text='e.g. blog, story or article', verbose_name='URL', max_length=16)),
                ('has_index', models.BooleanField(verbose_name='Has index', default=True)),
                ('visible', models.BooleanField(verbose_name='Visible', default=True)),
            ],
            options={
                'verbose_name_plural': 'content types',
                'verbose_name': 'content type',
            },
        ),
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], verbose_name='language', max_length=15)),
                ('name', models.CharField(verbose_name='Name', max_length=48)),
                ('plural', models.CharField(verbose_name='Plural', default='__', max_length=48)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name_plural': 'translations',
                'verbose_name': 'translation',
            },
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('object_id', models.PositiveIntegerField(db_index=True, verbose_name='Object Id', null=True)),
                ('moderated', models.NullBooleanField(verbose_name='Moderated', default=None)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('accepted', models.BooleanField(verbose_name='Accepted', default=False, editable=False)),
                ('name', models.CharField(verbose_name='Name', max_length=24)),
                ('body', models.TextField(verbose_name='Body')),
                ('url', models.URLField(blank=True, verbose_name='URL', max_length=100)),
                ('email', models.EmailField(blank=True, verbose_name='Email', max_length=64)),
                ('spam', models.NullBooleanField(db_index=True, verbose_name='Spam', default=None)),
                ('updated', models.DateTimeField(db_index=True, verbose_name='Updated', default=None, null=True)),
                ('visible', models.BooleanField(db_index=True, verbose_name='Visible', default=True)),
                ('removed', models.BooleanField(verbose_name='Removed', default=False, help_text='When visible, mark as removed')),
            ],
            options={
                'verbose_name_plural': 'comments',
                'verbose_name': 'comment',
                'permissions': (('can_edit_own_comment', 'Can edit own Comment'),),
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('se_indexed', models.BooleanField(db_index=True, verbose_name='Index in search engines', default=False)),
                ('data', picklefield.fields.PickledObjectField(verbose_name='Data', default=dict, editable=False)),
                ('object_id', models.PositiveIntegerField(blank=True, db_index=True, verbose_name='Object Id', null=True)),
                ('moderated', models.NullBooleanField(verbose_name='Moderated', default=None)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('access', models.SmallIntegerField(choices=[[0, 'Public'], [1, 'Friends'], [2, 'Personal'], [3, 'Friend groups'], [4, 'Registered users']], db_index=True, verbose_name='Access', default=0)),
                ('commentable', models.BooleanField(db_index=True, verbose_name='Commentable', default=True)),
                ('comment_count', models.IntegerField(verbose_name='Comments', default=0)),
                ('title', models.CharField(verbose_name='Title', max_length=192)),
                ('body', models.TextField(blank=True, verbose_name='Text')),
                ('html', models.TextField(blank=True, verbose_name='HTML', help_text='HTML output from body')),
                ('teaser', models.TextField(blank=True, verbose_name='Introduction')),
                ('format', models.SmallIntegerField(choices=[(0, 'Plain HTML'), (1, 'Markdown'), (2, 'Textile')], verbose_name='Format', default=0)),
                ('slug', autoslug.fields.AutoSlugField(populate_from='title', blank=True, unique_with=('id',), editable=True, max_length=100)),
                ('deleted', models.BooleanField(db_index=True, verbose_name='Deleted', default=False)),
                ('created', models.DateTimeField(db_index=True, verbose_name='Created', default=django.utils.timezone.now)),
                ('edited', models.DateTimeField(db_index=True, verbose_name='Edited', default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(db_index=True, verbose_name='Updated', default=django.utils.timezone.now)),
                ('publish', models.DateTimeField(blank=True, verbose_name='Publish when', null=True)),
                ('expire', models.DateTimeField(blank=True, verbose_name='Unpublish when', null=True)),
                ('published', models.BooleanField(db_index=True, verbose_name='Published', default=True)),
                ('sticky', models.BooleanField(db_index=True, verbose_name='Sticky', default=False, help_text='Will stay on top of lists')),
                ('featured', models.BooleanField(db_index=True, verbose_name='Featured', default=False, help_text='Will appear in magazine editorial content')),
                ('locked', models.BooleanField(db_index=True, verbose_name='Locked', default=False)),
            ],
            options={
                'verbose_name_plural': 'contents',
                'verbose_name': 'content',
                'permissions': (('can_access_all_content', 'Can bypass content access'),),
                'ordering': ['-edited'],
                'get_latest_by': 'updated',
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('object_id', models.PositiveIntegerField(blank=True, db_index=True, verbose_name='Object Id', null=True)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field='icon_height', verbose_name='Icon', max_length=96, blank=True, upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, width_field='icon_width', help_text='Maximum size 64x64')),
                ('icon_width', models.IntegerField(blank=True, verbose_name='Width', null=True, editable=False)),
                ('icon_height', models.IntegerField(blank=True, verbose_name='Height', null=True, editable=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('group', models.CharField(blank=True, db_index=True, verbose_name='Group', help_text='Use the same name to group icons.', max_length=16)),
                ('display', models.SmallIntegerField(choices=[(0, 'Text'), (1, 'Icon'), (2, 'Icon and text'), (3, 'oEmbed'), (4, 'Flash')], db_index=True, verbose_name='Type', default=0, help_text='Default display mode of this link')),
                ('url', models.URLField(unique=True, verbose_name='URL', max_length=1024)),
                ('anchor', models.CharField(blank=True, verbose_name='Anchor', max_length=192)),
                ('title', models.CharField(blank=True, verbose_name='Title', max_length=128)),
                ('target', models.CharField(blank=True, verbose_name='Target', default='_self', max_length=16)),
                ('nofollow', models.BooleanField(verbose_name='No-follow', default=True)),
                ('remainder', models.CharField(blank=True, help_text='HTML code of extra tag attributes', verbose_name='HTML Remainder', max_length=64)),
                ('information', models.TextField(blank=True, verbose_name='Information', default='', help_text='Internal information for the link')),
                ('description', models.TextField(blank=True, verbose_name='Description', default='')),
            ],
            options={
                'verbose_name_plural': 'links',
                'verbose_name': 'link',
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('moderated', models.NullBooleanField(verbose_name='Moderated', default=None)),
                ('width', models.IntegerField(blank=True, verbose_name='Width', default=0, null=True)),
                ('height', models.IntegerField(blank=True, verbose_name='Height', default=0, null=True)),
                ('weight', models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)], db_index=True, verbose_name='Weight', default=10, help_text='Items with lower weights come first')),
                ('license', models.CharField(blank=True, verbose_name='License/Creator', default=';', max_length=40)),
                ('audience', models.SmallIntegerField(choices=[(0, 'Everyone'), (5, 'Adults only')], verbose_name='Audience rating', default=0)),
                ('image', scoop.core.util.model.fields.WebImageField(height_field='height', db_index=True, verbose_name='Image', max_length=200, upload_to=scoop.content.util.picture.get_image_upload_path, width_field='width', help_text='Only .gif, .jpeg or .png image files, 64x64 minimum')),
                ('title', models.CharField(blank=True, verbose_name='Title', max_length=96)),
                ('description', models.TextField(blank=True, verbose_name='Description', help_text='Description text. Enter an URL here to download a picture')),
                ('marker', models.CharField(blank=True, help_text='Comma separated', verbose_name='Internal marker', max_length=36)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=48, unique=True, max_length=8, default='', editable=False)),
                ('deleted', models.BooleanField(verbose_name='Deleted', default=False)),
                ('animated', models.BooleanField(verbose_name='Animated', default=False)),
                ('transient', models.BooleanField(verbose_name='Transient', default=False)),
                ('updated', models.DateTimeField(verbose_name='Updated', default=django.utils.timezone.now)),
                ('object_id', models.PositiveIntegerField(blank=True, verbose_name='Object Id', null=True)),
            ],
            options={
                'verbose_name_plural': 'images',
                'verbose_name': 'image',
                'permissions': [['can_upload_picture', 'Can upload a picture'], ['can_moderate_picture', 'Can moderate pictures']],
            },
            bases=(models.Model, scoop.core.abstract.core.rectangle.RectangleObject),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field='icon_height', verbose_name='Icon', max_length=96, blank=True, upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, width_field='icon_width', help_text='Maximum size 64x64')),
                ('icon_width', models.IntegerField(blank=True, verbose_name='Width', null=True, editable=False)),
                ('icon_height', models.IntegerField(blank=True, verbose_name='Height', null=True, editable=False)),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('group', models.CharField(blank=True, verbose_name='Group', max_length=16)),
                ('name', models.CharField(verbose_name='Name', max_length=96)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('short_name', autoslug.fields.AutoSlugField(populate_from='name', verbose_name='Short name', blank=True, unique_with=('id',), editable=True)),
                ('active', models.BooleanField(verbose_name='Active', default=True)),
                ('category', models.ForeignKey(to='content.Category', null=True, verbose_name='Category', help_text='Category if this tag is specific to one')),
                ('parent', models.ForeignKey(related_name='children', to='content.Tag', verbose_name='Parent', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'tags',
                'verbose_name': 'tag',
                'ordering': ['name'],
            },
        ),
    ]
