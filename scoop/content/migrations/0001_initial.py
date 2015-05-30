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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field=b'icon_height', width_field=b'icon_width', upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, max_length=96, blank=True, help_text='Taille maximum 64x64', verbose_name='Icon')),
                ('icon_width', models.IntegerField(verbose_name='Width', null=True, editable=False, blank=True)),
                ('icon_height', models.IntegerField(verbose_name='Height', null=True, editable=False, blank=True)),
                ('width', models.IntegerField(default=0, null=True, verbose_name='Width', blank=True)),
                ('height', models.IntegerField(default=0, null=True, verbose_name='Height', blank=True)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('name', models.CharField(unique=True, max_length=32, verbose_name='Name')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('group', models.CharField(help_text='Pipe separated', max_length=48, verbose_name='Group name', blank=True)),
                ('code', models.TextField(help_text='Django template code for HTML/JS', verbose_name='HTML/JS Snippet')),
                ('views', models.IntegerField(default=0, verbose_name='Views', editable=False)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('network', models.CharField(default=b'na', max_length=4, verbose_name='Ad network', db_index=True, choices=[[b'gg', 'Google Adsense'], [b'af', 'AdFever'], [b'na', 'Custom'], [b'ot', 'Other']])),
            ],
            options={
                'verbose_name': 'advertisement',
                'verbose_name_plural': 'advertisements',
            },
            bases=(models.Model, scoop.core.abstract.core.rectangle.RectangleObject),
        ),
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('object_id', models.PositiveIntegerField(db_index=True, null=True, verbose_name='Object Id', blank=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('access', models.SmallIntegerField(default=0, db_index=True, verbose_name='Access', choices=[[0, 'Public'], [1, 'Friends'], [2, 'Personal'], [3, 'Friend groups'], [4, 'Registered users']])),
                ('name', models.CharField(max_length=96, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
                ('visible', models.BooleanField(default=True, verbose_name='Visible')),
            ],
            options={
                'verbose_name': 'picture album',
                'verbose_name_plural': 'picture albums',
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.CreateModel(
            name='Animation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=128, unique=True, max_length=22, editable=False)),
                ('file', models.FileField(upload_to=scoop.content.util.picture.get_animation_upload_path, max_length=192, verbose_name='File')),
                ('extension', models.CharField(default=b'mp4', max_length=8, verbose_name='Extension')),
                ('duration', models.FloatField(default=0.0, help_text='In seconds', verbose_name='Duration', editable=False, db_index=True)),
                ('title', models.CharField(max_length=96, verbose_name='Title', blank=True)),
                ('description', models.TextField(help_text='Description text. Enter an URL here to download a picture', verbose_name='Description', blank=True)),
                ('autoplay', models.BooleanField(default=False, verbose_name='Auto play')),
                ('loop', models.BooleanField(default=True, verbose_name='Loop')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
            ],
            options={
                'verbose_name': 'Animation',
                'verbose_name_plural': 'Animations',
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('group', models.CharField(db_index=True, max_length=16, verbose_name='Group', blank=True)),
                ('file', models.FileField(help_text='File to attach', upload_to=scoop.content.util.attachment.get_attachment_upload_path, max_length=192, verbose_name='File')),
                ('name', models.CharField(max_length=64, verbose_name='Name', blank=True)),
                ('description', models.TextField(default='', verbose_name='Description', blank=True)),
                ('mimetype', models.CharField(max_length=40, verbose_name='MIME type', blank=True)),
                ('object_id', models.PositiveIntegerField(db_index=True, null=True, verbose_name='Object Id', blank=True)),
            ],
            options={
                'verbose_name': 'attachment',
                'verbose_name_plural': 'attachments',
                'permissions': (('can_join_files', 'Can join files'),),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field=b'icon_height', width_field=b'icon_width', upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, max_length=96, blank=True, help_text='Taille maximum 64x64', verbose_name='Icon')),
                ('icon_width', models.IntegerField(verbose_name='Width', null=True, editable=False, blank=True)),
                ('icon_height', models.IntegerField(verbose_name='Height', null=True, editable=False, blank=True)),
                ('short_name', models.CharField(max_length=10, verbose_name='Identifier')),
                ('url', models.CharField(help_text='e.g. blog, story or article', max_length=16, verbose_name='URL')),
                ('has_index', models.BooleanField(default=True, verbose_name='Has index')),
                ('visible', models.BooleanField(default=True, verbose_name='Visible')),
            ],
            options={
                'verbose_name': 'content type',
                'verbose_name_plural': 'content types',
            },
        ),
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=15, verbose_name='language', choices=[(b'en', 'English'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=48, verbose_name='Name')),
                ('plural', models.CharField(default=b'__', max_length=48, verbose_name='Plural')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
            ],
            options={
                'verbose_name': 'translation',
                'verbose_name_plural': 'translations',
            },
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='Object Id', db_index=True)),
                ('moderated', models.NullBooleanField(default=None, verbose_name='Moderated')),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('accepted', models.BooleanField(default=False, verbose_name='Accepted', editable=False)),
                ('name', models.CharField(max_length=24, verbose_name='Name')),
                ('body', models.TextField(verbose_name='Body')),
                ('url', models.URLField(max_length=100, verbose_name='URL', blank=True)),
                ('email', models.EmailField(max_length=64, verbose_name='Email', blank=True)),
                ('spam', models.BooleanField(default=False, db_index=True, verbose_name='Spam')),
                ('updated', models.DateTimeField(default=None, null=True, verbose_name='Updated', db_index=True)),
                ('visible', models.BooleanField(default=True, db_index=True, verbose_name='Visible')),
                ('removed', models.BooleanField(default=False, help_text='When visible, mark as removed', verbose_name='Removed')),
            ],
            options={
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'permissions': (('can_edit_own_comment', 'Can edit own Comment'),),
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('se_indexed', models.BooleanField(default=False, db_index=True, verbose_name='Index in search engines')),
                ('data', picklefield.fields.PickledObjectField(default=dict, verbose_name='Data', editable=False)),
                ('object_id', models.PositiveIntegerField(db_index=True, null=True, verbose_name='Object Id', blank=True)),
                ('moderated', models.NullBooleanField(default=None, verbose_name='Moderated')),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('access', models.SmallIntegerField(default=0, db_index=True, verbose_name='Access', choices=[[0, 'Public'], [1, 'Friends'], [2, 'Personal'], [3, 'Friend groups'], [4, 'Registered users']])),
                ('commentable', models.BooleanField(default=True, db_index=True, verbose_name='Commentable')),
                ('comment_count', models.IntegerField(default=0, verbose_name='Comments')),
                ('title', models.CharField(max_length=192, verbose_name='Title')),
                ('body', models.TextField(verbose_name='Text', blank=True)),
                ('html', models.TextField(help_text='HTML output from body', verbose_name='HTML', blank=True)),
                ('teaser', models.TextField(verbose_name='Introduction', blank=True)),
                ('format', models.SmallIntegerField(default=0, verbose_name='Format', choices=[(0, 'Plain HTML'), (1, 'Markdown'), (2, 'Textile')])),
                ('slug', autoslug.fields.AutoSlugField(max_length=100, blank=True)),
                ('deleted', models.BooleanField(default=False, db_index=True, verbose_name='Deleted')),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created', db_index=True)),
                ('edited', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Edited', db_index=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Updated', db_index=True)),
                ('publish', models.DateTimeField(null=True, verbose_name='Publish when', blank=True)),
                ('expire', models.DateTimeField(null=True, verbose_name='Unpublish when', blank=True)),
                ('published', models.BooleanField(default=True, db_index=True, verbose_name='Published')),
                ('sticky', models.BooleanField(default=False, help_text='Will stay on top of lists', db_index=True, verbose_name='Sticky')),
                ('featured', models.BooleanField(default=False, help_text='Will appear in magazine editorial content', db_index=True, verbose_name='Featured')),
                ('locked', models.BooleanField(default=False, db_index=True, verbose_name='Locked')),
            ],
            options={
                'ordering': ['-edited'],
                'get_latest_by': 'updated',
                'verbose_name': 'content',
                'verbose_name_plural': 'contents',
                'permissions': (('can_access_all_content', 'Can bypass content access'),),
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('object_id', models.PositiveIntegerField(db_index=True, null=True, verbose_name='Object Id', blank=True)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field=b'icon_height', width_field=b'icon_width', upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, max_length=96, blank=True, help_text='Taille maximum 64x64', verbose_name='Icon')),
                ('icon_width', models.IntegerField(verbose_name='Width', null=True, editable=False, blank=True)),
                ('icon_height', models.IntegerField(verbose_name='Height', null=True, editable=False, blank=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('group', models.CharField(help_text='Use the same name to group icons.', max_length=16, verbose_name='Group', db_index=True, blank=True)),
                ('display', models.SmallIntegerField(default=0, help_text='Default display mode of this link', db_index=True, verbose_name='Type', choices=[(0, 'Text'), (1, 'Icon'), (2, 'Icon and text'), (3, 'oEmbed'), (4, 'Flash')])),
                ('url', models.URLField(unique=True, max_length=1024, verbose_name='URL')),
                ('anchor', models.CharField(max_length=192, verbose_name='Anchor', blank=True)),
                ('title', models.CharField(max_length=128, verbose_name='Title', blank=True)),
                ('target', models.CharField(default=b'_self', max_length=16, verbose_name='Target', blank=True)),
                ('nofollow', models.BooleanField(default=True, verbose_name='No-follow')),
                ('remainder', models.CharField(help_text='HTML code of extra tag attributes', max_length=64, verbose_name='HTML Remainder', blank=True)),
                ('information', models.TextField(default='', help_text='Internal information for the link', verbose_name='Information', blank=True)),
                ('description', models.TextField(default='', verbose_name='Description', blank=True)),
            ],
            options={
                'verbose_name': 'link',
                'verbose_name_plural': 'links',
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('moderated', models.NullBooleanField(default=None, verbose_name='Moderated')),
                ('width', models.IntegerField(default=0, null=True, verbose_name='Width', blank=True)),
                ('height', models.IntegerField(default=0, null=True, verbose_name='Height', blank=True)),
                ('weight', models.SmallIntegerField(default=10, help_text='Items with lower weights come first', db_index=True, verbose_name='Weight', choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 11), (12, 12), (13, 13), (14, 14), (15, 15), (16, 16), (17, 17), (18, 18), (19, 19), (20, 20), (21, 21), (22, 22), (23, 23), (24, 24), (25, 25), (26, 26), (27, 27), (28, 28), (29, 29), (30, 30), (31, 31), (32, 32), (33, 33), (34, 34), (35, 35), (36, 36), (37, 37), (38, 38), (39, 39), (40, 40), (41, 41), (42, 42), (43, 43), (44, 44), (45, 45), (46, 46), (47, 47), (48, 48), (49, 49), (50, 50), (51, 51), (52, 52), (53, 53), (54, 54), (55, 55), (56, 56), (57, 57), (58, 58), (59, 59), (60, 60), (61, 61), (62, 62), (63, 63), (64, 64), (65, 65), (66, 66), (67, 67), (68, 68), (69, 69), (70, 70), (71, 71), (72, 72), (73, 73), (74, 74), (75, 75), (76, 76), (77, 77), (78, 78), (79, 79), (80, 80), (81, 81), (82, 82), (83, 83), (84, 84), (85, 85), (86, 86), (87, 87), (88, 88), (89, 89), (90, 90), (91, 91), (92, 92), (93, 93), (94, 94), (95, 95), (96, 96), (97, 97), (98, 98), (99, 99)])),
                ('license', models.CharField(default=';', max_length=40, verbose_name='License/Creator', blank=True)),
                ('audience', models.SmallIntegerField(default=0, verbose_name='Audience rating', choices=[(0, 'Everyone'), (5, 'Adults only')])),
                ('image', scoop.core.util.model.fields.WebImageField(height_field=b'height', width_field=b'width', upload_to=scoop.content.util.picture.get_image_upload_path, max_length=200, help_text='Only .gif, .jpeg or .png image files, 64x64 minimum', verbose_name='Image', db_index=True)),
                ('title', models.CharField(max_length=96, verbose_name='Title', blank=True)),
                ('description', models.TextField(help_text='Description text. Enter an URL here to download a picture', verbose_name='Description', blank=True)),
                ('marker', models.CharField(help_text='Comma separated', max_length=36, verbose_name='Internal marker', blank=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=48, unique=True, max_length=8, editable=False)),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted')),
                ('animated', models.BooleanField(default=False, verbose_name='Animated')),
                ('transient', models.BooleanField(default=False, verbose_name='Transient')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Updated')),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='Object Id', blank=True)),
            ],
            options={
                'permissions': [['can_upload_picture', 'Can upload a picture']],
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
            },
            bases=(models.Model, scoop.core.abstract.core.rectangle.RectangleObject),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('icon', easy_thumbnails.fields.ThumbnailerImageField(height_field=b'icon_height', width_field=b'icon_width', upload_to=scoop.core.abstract.core.icon.get_icon_upload_path, max_length=96, blank=True, help_text='Taille maximum 64x64', verbose_name='Icon')),
                ('icon_width', models.IntegerField(verbose_name='Width', null=True, editable=False, blank=True)),
                ('icon_height', models.IntegerField(verbose_name='Height', null=True, editable=False, blank=True)),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('group', models.CharField(max_length=16, verbose_name='Group', blank=True)),
                ('name', models.CharField(max_length=96, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('short_name', autoslug.fields.AutoSlugField(max_length=100, verbose_name='Short name', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('category', models.ForeignKey(verbose_name='Category', to='content.Category', help_text='Category if this tag is specific to one', null=True)),
                ('parent', models.ForeignKey(related_name='children', verbose_name='Parent', blank=True, to='content.Tag', null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
        ),
    ]
