# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='picture',
            options={'verbose_name': 'image', 'verbose_name_plural': 'images', 'permissions': [['can_upload_picture', 'Can upload a picture']]},
        ),
    ]
