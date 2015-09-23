# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models

import scoop.core.abstract.core.generic
import scoop.core.abstract.core.translation
import scoop.core.abstract.core.uuid
import scoop.core.util.data.dateutil


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('codename', models.CharField(verbose_name='Code name', max_length=32)),
                ('sentence', models.CharField(verbose_name='Sentence', max_length=48)),
                ('verb', models.CharField(verbose_name='Verb', max_length=24)),
            ],
            options={
                'verbose_name_plural': 'action types',
                'verbose_name': 'action type',
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('uuid', scoop.core.abstract.core.uuid.UUIDField(bits=64, unique=True, max_length=11, default='', editable=False)),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('code', models.SmallIntegerField(choices=[[0, 0], [1, 1], [2, 2], [3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [8, 8], [9, 9], [10, 10], [11, 11], [12, 12], [13, 13], [14, 14], [15, 15], [16, 16], [17, 17], [18, 18], [19, 19], [20, 20], [21, 21], [22, 22], [23, 23], [24, 24], [25, 25], [26, 26], [27, 27], [28, 28], [29, 29], [30, 30], [31, 31], [32, 32], [33, 33], [34, 34], [35, 35], [36, 36], [37, 37], [38, 38], [39, 39], [40, 40], [41, 41], [42, 42], [43, 43], [44, 44], [45, 45], [46, 46], [47, 47], [48, 48], [49, 49], [50, 50], [51, 51], [52, 52], [53, 53], [54, 54], [55, 55], [56, 56], [57, 57], [58, 58], [59, 59], [60, 60], [61, 61], [62, 62], [63, 63], [64, 64], [65, 65], [66, 66], [67, 67], [68, 68], [69, 69], [70, 70], [71, 71], [72, 72], [73, 73], [74, 74], [75, 75], [76, 76], [77, 77], [78, 78], [79, 79], [80, 80], [81, 81], [82, 82], [83, 83], [84, 84], [85, 85], [86, 86], [87, 87], [88, 88], [89, 89], [90, 90], [91, 91], [92, 92], [93, 93], [94, 94], [95, 95], [96, 96], [97, 97], [98, 98], [99, 99], [100, 100], [101, 101], [102, 102], [103, 103], [104, 104], [105, 105], [106, 106], [107, 107], [108, 108], [109, 109], [110, 110], [111, 111], [112, 112], [113, 113], [114, 114], [115, 115], [116, 116], [117, 117], [118, 118], [119, 119], [120, 120], [121, 121], [122, 122], [123, 123], [124, 124], [125, 125], [126, 126], [127, 127], [128, 128], [129, 129], [130, 130], [131, 131], [132, 132], [133, 133], [134, 134], [135, 135], [136, 136], [137, 137], [138, 138], [139, 139], [140, 140], [141, 141], [142, 142], [143, 143], [144, 144], [145, 145], [146, 146], [147, 147], [148, 148], [149, 149], [150, 150], [151, 151], [152, 152], [153, 153], [154, 154], [155, 155], [156, 156], [157, 157], [158, 158], [159, 159], [160, 160], [161, 161], [162, 162], [163, 163], [164, 164], [165, 165], [166, 166], [167, 167], [168, 168], [169, 169], [170, 170], [171, 171], [172, 172], [173, 173], [174, 174], [175, 175], [176, 176], [177, 177], [178, 178], [179, 179], [180, 180], [181, 181], [182, 182], [183, 183], [184, 184], [185, 185], [186, 186], [187, 187], [188, 188], [189, 189], [190, 190], [191, 191], [192, 192], [193, 193], [194, 194], [195, 195], [196, 196], [197, 197], [198, 198], [199, 199]], db_index=True, verbose_name='Code')),
                ('active', models.BooleanField(verbose_name='Active', default=True)),
            ],
            options={
                'verbose_name_plural': 'options',
                'verbose_name': 'option',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='OptionGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('pictured', models.BooleanField(db_index=True, verbose_name='\U0001f58c', default=False)),
                ('code', models.SmallIntegerField(verbose_name='Code', default=0)),
                ('short_name', models.CharField(verbose_name='Short name', max_length=20)),
            ],
            options={
                'verbose_name_plural': 'option groups',
                'verbose_name': 'option group',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='OptionGroupTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], verbose_name='language', max_length=15)),
                ('name', models.CharField(verbose_name='Name', max_length=80)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='OptionTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('language', models.CharField(choices=[('en', 'English'), ('fr', 'French')], verbose_name='language', max_length=15)),
                ('name', models.CharField(verbose_name='Name', max_length=120)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            bases=(models.Model, scoop.core.abstract.core.translation.TranslationModel),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Name', max_length=32)),
                ('created', models.DateTimeField(db_index=True, verbose_name='Created', auto_now_add=True)),
                ('target_id', models.PositiveIntegerField(db_index=True, verbose_name='Target Id', null=True)),
                ('target_name', models.CharField(verbose_name='Target name', max_length=80)),
                ('container_id', models.PositiveIntegerField(db_index=True, verbose_name='Container Id', null=True)),
                ('container_name', models.CharField(verbose_name='Container name', max_length=80)),
                ('container_type', models.ForeignKey(related_name='container_record', to='contenttypes.ContentType', null=True, verbose_name='Container type')),
                ('target_type', models.ForeignKey(related_name='target_record', to='contenttypes.ContentType', null=True, verbose_name='Target type')),
                ('type', models.ForeignKey(related_name='records', to='core.ActionType', verbose_name='Action type')),
            ],
            options={
                'verbose_name_plural': 'records',
                'verbose_name': 'record',
            },
        ),
        migrations.CreateModel(
            name='Redirection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('active', models.BooleanField(db_index=True, verbose_name='Active', default=True)),
                ('base', models.CharField(unique=True, verbose_name='Original URL', max_length=250)),
                ('expires', models.DateTimeField(verbose_name='Expiry', default=datetime.datetime(2025, 9, 3, 8, 16, 13, 838648))),
                ('permanent', models.BooleanField(verbose_name='Permanent', default=True)),
                ('object_id', models.PositiveIntegerField(db_index=True, verbose_name='Object Id', null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True, verbose_name='Content type')),
            ],
            options={
                'verbose_name_plural': 'redirections',
                'verbose_name': 'redirection',
            },
            bases=(scoop.core.abstract.core.generic.GenericModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UUIDEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('object_id', models.PositiveIntegerField(db_index=True, verbose_name='Object Id', null=True)),
                ('uuid', models.CharField(unique=True, verbose_name='UUID', max_length=22)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True, verbose_name='Content type')),
            ],
            options={
                'verbose_name_plural': 'UUID References',
                'verbose_name': 'UUID Reference',
            },
            bases=(models.Model, scoop.core.abstract.core.generic.GenericModelMixin),
        ),
    ]
