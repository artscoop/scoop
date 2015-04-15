# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import scoop.core.util.data.dateutil


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codename', models.CharField(max_length=32, verbose_name='Code name')),
                ('sentence', models.CharField(max_length=48, verbose_name='Sentence')),
                ('verb', models.CharField(max_length=24, verbose_name='Verb')),
            ],
            options={
                'verbose_name': 'action type',
                'verbose_name_plural': 'action types',
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(default='', bits=64, unique=True, max_length=11, editable=False)),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('code', models.SmallIntegerField(db_index=True, verbose_name='Code', choices=[[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10], [11, 11], [12, 12], [13, 13], [14, 14], [15, 15], [16, 16], [17, 17], [18, 18], [19, 19], [20, 20], [21, 21], [22, 22], [23, 23], [24, 24], [25, 25], [26, 26], [27, 27], [28, 28], [29, 29], [30, 30], [31, 31], [32, 32], [33, 33], [34, 34], [35, 35], [36, 36], [37, 37], [38, 38], [39, 39], [40, 40], [41, 41], [42, 42], [43, 43], [44, 44], [45, 45], [46, 46], [47, 47], [48, 48], [49, 49], [50, 50], [51, 51], [52, 52], [53, 53], [54, 54], [55, 55], [56, 56], [57, 57], [58, 58], [59, 59], [60, 60], [61, 61], [62, 62], [63, 63], [64, 64], [65, 65], [66, 66], [67, 67], [68, 68], [69, 69], [70, 70], [71, 71], [72, 72], [73, 73], [74, 74], [75, 75], [76, 76], [77, 77], [78, 78], [79, 79], [80, 80], [81, 81], [82, 82], [83, 83], [84, 84], [85, 85], [86, 86], [87, 87], [88, 88], [89, 89], [90, 90], [91, 91], [92, 92], [93, 93], [94, 94], [95, 95], [96, 96], [97, 97], [98, 98], [99, 99], [100, 100], [101, 101], [102, 102], [103, 103], [104, 104], [105, 105], [106, 106], [107, 107], [108, 108], [109, 109], [110, 110], [111, 111], [112, 112], [113, 113], [114, 114], [115, 115], [116, 116], [117, 117], [118, 118], [119, 119], [120, 120], [121, 121], [122, 122], [123, 123], [124, 124], [125, 125], [126, 126], [127, 127], [128, 128], [129, 129], [130, 130], [131, 131], [132, 132], [133, 133], [134, 134], [135, 135], [136, 136], [137, 137], [138, 138], [139, 139], [140, 140], [141, 141], [142, 142], [143, 143], [144, 144], [145, 145], [146, 146], [147, 147], [148, 148], [149, 149], [150, 150], [151, 151], [152, 152], [153, 153], [154, 154], [155, 155], [156, 156], [157, 157], [158, 158], [159, 159], [160, 160], [161, 161], [162, 162], [163, 163], [164, 164], [165, 165], [166, 166], [167, 167], [168, 168], [169, 169], [170, 170], [171, 171], [172, 172], [173, 173], [174, 174], [175, 175], [176, 176], [177, 177], [178, 178], [179, 179], [180, 180], [181, 181], [182, 182], [183, 183], [184, 184], [185, 185], [186, 186], [187, 187], [188, 188], [189, 189], [190, 190], [191, 191], [192, 192], [193, 193], [194, 194], [195, 195], [196, 196], [197, 197], [198, 198], [199, 199]])),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'ordering': ['code'],
                'verbose_name': 'option',
                'verbose_name_plural': 'options',
            },
        ),
        migrations.CreateModel(
            name='OptionGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictured', models.BooleanField(default=False, db_index=True, verbose_name='\U0001f58c')),
                ('code', models.SmallIntegerField(default=0, verbose_name='Code', choices=[[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10], [11, 11], [12, 12], [13, 13], [14, 14], [15, 15], [16, 16], [17, 17], [18, 18], [19, 19], [20, 20], [21, 21], [22, 22], [23, 23], [24, 24], [25, 25], [26, 26], [27, 27], [28, 28], [29, 29], [30, 30], [31, 31], [32, 32], [33, 33], [34, 34], [35, 35], [36, 36], [37, 37], [38, 38], [39, 39], [40, 40], [41, 41], [42, 42], [43, 43], [44, 44], [45, 45], [46, 46], [47, 47], [48, 48], [49, 49], [50, 50], [51, 51], [52, 52], [53, 53], [54, 54], [55, 55], [56, 56], [57, 57], [58, 58], [59, 59], [60, 60], [61, 61], [62, 62], [63, 63], [64, 64], [65, 65], [66, 66], [67, 67], [68, 68], [69, 69], [70, 70], [71, 71], [72, 72], [73, 73], [74, 74], [75, 75], [76, 76], [77, 77], [78, 78], [79, 79], [80, 80], [81, 81], [82, 82], [83, 83], [84, 84], [85, 85], [86, 86], [87, 87], [88, 88], [89, 89], [90, 90], [91, 91], [92, 92], [93, 93], [94, 94], [95, 95], [96, 96], [97, 97], [98, 98], [99, 99]])),
                ('short_name', models.CharField(max_length=20, verbose_name='Short name')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'option group',
                'verbose_name_plural': 'option groups',
            },
        ),
        migrations.CreateModel(
            name='OptionGroupTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=15, verbose_name='language', choices=[(b'en', 'English'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('model', models.ForeignKey(related_name='translations', verbose_name=b'optiongroup', to='core.OptionGroup')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='OptionTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=15, verbose_name='language', choices=[(b'en', 'English'), (b'fr', 'French')])),
                ('name', models.CharField(max_length=120, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('model', models.ForeignKey(related_name='translations', verbose_name=b'option', to='core.Option')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='Name')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created', db_index=True)),
                ('target_id', models.PositiveIntegerField(null=True, verbose_name='Target Id', db_index=True)),
                ('target_name', models.CharField(max_length=80, verbose_name='Target name')),
                ('container_id', models.PositiveIntegerField(null=True, verbose_name='Container Id', db_index=True)),
                ('container_name', models.CharField(max_length=80, verbose_name='Container name')),
                ('container_type', models.ForeignKey(related_name='container_record', verbose_name='Container type', to='contenttypes.ContentType', null=True)),
                ('target_type', models.ForeignKey(related_name='target_record', verbose_name='Target type', to='contenttypes.ContentType', null=True)),
                ('type', models.ForeignKey(related_name='records', verbose_name='Action type', to='core.ActionType')),
                ('user', models.ForeignKey(related_name='action_records', on_delete=django.db.models.deletion.SET_NULL, verbose_name='User', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'record',
                'verbose_name_plural': 'records',
            },
        ),
        migrations.CreateModel(
            name='Redirection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('active', models.BooleanField(default=True, db_index=True, verbose_name='Active')),
                ('base', models.CharField(unique=True, max_length=250, verbose_name='Original URL')),
                ('expires', models.DateTimeField(default=datetime.datetime(2025, 4, 3, 14, 31, 35, 833605), verbose_name='Expiry')),
                ('permanent', models.BooleanField(default=True, verbose_name='Permanent')),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='Object Id', db_index=True)),
                ('content_type', models.ForeignKey(verbose_name='Content type', to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name': 'redirection',
                'verbose_name_plural': 'redirections',
            },
            bases=(scoop.core.abstract.core.generic.GenericModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UUIDEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='Object Id', db_index=True)),
                ('uuid', models.CharField(unique=True, max_length=22, verbose_name='UUID')),
                ('content_type', models.ForeignKey(verbose_name='Content type', to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name': 'UUID Reference',
                'verbose_name_plural': 'UUID References',
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
        migrations.AddField(
            model_name='option',
            name='group',
            field=models.ForeignKey(related_name='options', verbose_name='Group', to='core.OptionGroup'),
        ),
        migrations.AddField(
            model_name='option',
            name='parent',
            field=models.ForeignKey(related_name='children', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Parent', blank=True, to='core.Option', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('group', 'code')]),
        ),
    ]
