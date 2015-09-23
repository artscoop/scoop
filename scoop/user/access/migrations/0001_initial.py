# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models

import scoop.core.util.data.dateutil


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('referrer', models.CharField(verbose_name='Referrer', max_length=192)),
            ],
            options={
                'verbose_name_plural': 'accesses',
                'verbose_name': 'access',
            },
        ),
        migrations.CreateModel(
            name='IP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=4326, default=(0.0, 0.0))),
                ('ip', models.DecimalField(unique=True, db_index=True, verbose_name='Decimal', blank=True, decimal_places=0, max_digits=39)),
                ('string', models.CharField(verbose_name='String', max_length=48)),
                ('reverse', models.CharField(blank=True, verbose_name='Reverse', max_length=80)),
                ('status', models.SmallIntegerField(choices=[[0, 'Ok'], [1, 'Timed out'], [2, 'Empty answer'], [3, 'Broken NS'], [4, 'Domain not found']], verbose_name='Reverse status', default=0)),
                ('isp', models.CharField(blank=True, verbose_name='ISP', max_length=64)),
                ('country', models.CharField(choices=[('AL', 'Albania'), ('BN', 'Brunei Darussalam'), ('GU', 'Guam'), ('AO', 'Angola'), ('YE', 'Yemen'), ('TF', 'French Southern Territories'), ('BB', 'Barbados'), ('BS', 'Bahamas'), ('MU', 'Mauritius'), ('LI', 'Liechtenstein'), ('BM', 'Bermuda'), ('PL', 'Poland'), ('GS', 'South Georgia and the South Sandwich Islands'), ('UM', 'United States Minor Outlying Islands'), ('DJ', 'Djibouti'), ('TK', 'Tokelau'), ('HM', 'Heard Island and McDonald Islands'), ('CY', 'Cyprus'), ('CW', 'Curaçao'), ('CI', "Côte d'Ivoire"), ('PY', 'Paraguay'), ('NP', 'Nepal'), ('MN', 'Mongolia'), ('BE', 'Belgium'), ('ZW', 'Zimbabwe'), ('HN', 'Honduras'), ('GI', 'Gibraltar'), ('CG', 'Congo'), ('SK', 'Slovakia'), ('PE', 'Peru'), ('GL', 'Greenland'), ('BW', 'Botswana'), ('AU', 'Australia'), ('IL', 'Israel'), ('SY', 'Syrian Arab Republic'), ('BV', 'Bouvet Island'), ('CC', 'Cocos (Keeling) Islands'), ('CX', 'Christmas Island'), ('IN', 'India'), ('KM', 'Comoros'), ('UZ', 'Uzbekistan'), ('SN', 'Senegal'), ('ER', 'Eritrea'), ('SM', 'San Marino'), ('KZ', 'Kazakhstan'), ('KW', 'Kuwait'), ('ET', 'Ethiopia'), ('MQ', 'Martinique'), ('DZ', 'Algeria'), ('VN', 'Viet Nam'), ('HR', 'Croatia'), ('GM', 'Gambia'), ('CD', 'Congo (the Democratic Republic of the)'), ('MX', 'Mexico'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('MW', 'Malawi'), ('FJ', 'Fiji'), ('CU', 'Cuba'), ('GN', 'Guinea'), ('VI', 'Virgin Islands (U.S.)'), ('PF', 'French Polynesia'), ('RO', 'Romania'), ('AS', 'American Samoa'), ('BH', 'Bahrain'), ('PK', 'Pakistan'), ('PS', 'Palestine, State of'), ('FO', 'Faroe Islands'), ('BI', 'Burundi'), ('TR', 'Turkey'), ('NE', 'Niger'), ('IT', 'Italy'), ('LV', 'Latvia'), ('SG', 'Singapore'), ('TC', 'Turks and Caicos Islands'), ('GA', 'Gabon'), ('CA', 'Canada'), ('ZM', 'Zambia'), ('YT', 'Mayotte'), ('SR', 'Suriname'), ('DE', 'Germany'), ('AT', 'Austria'), ('IQ', 'Iraq'), ('TW', 'Taiwan (Province of China)'), ('UY', 'Uruguay'), ('TJ', 'Tajikistan'), ('BY', 'Belarus'), ('JP', 'Japan'), ('MR', 'Mauritania'), ('SZ', 'Swaziland'), ('KG', 'Kyrgyzstan'), ('SL', 'Sierra Leone'), ('SO', 'Somalia'), ('UG', 'Uganda'), ('KN', 'Saint Kitts and Nevis'), ('LA', "Lao People's Democratic Republic"), ('US', 'United States of America'), ('NU', 'Niue'), ('MG', 'Madagascar'), ('PM', 'Saint Pierre and Miquelon'), ('RW', 'Rwanda'), ('GY', 'Guyana'), ('MF', 'Saint Martin (French part)'), ('HK', 'Hong Kong'), ('CN', 'China'), ('GD', 'Grenada'), ('UA', 'Ukraine'), ('RS', 'Serbia'), ('FI', 'Finland'), ('NC', 'New Caledonia'), ('IS', 'Iceland'), ('NA', 'Namibia'), ('BO', 'Bolivia (Plurinational State of)'), ('SC', 'Seychelles'), ('NR', 'Nauru'), ('VC', 'Saint Vincent and the Grenadines'), ('NF', 'Norfolk Island'), ('CL', 'Chile'), ('TN', 'Tunisia'), ('CZ', 'Czech Republic'), ('MA', 'Morocco'), ('BT', 'Bhutan'), ('LT', 'Lithuania'), ('MK', 'Macedonia (the former Yugoslav Republic of)'), ('TZ', 'Tanzania, United Republic of'), ('TT', 'Trinidad and Tobago'), ('ID', 'Indonesia'), ('IO', 'British Indian Ocean Territory'), ('SE', 'Sweden'), ('ZA', 'South Africa'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('JM', 'Jamaica'), ('RU', 'Russian Federation'), ('VE', 'Venezuela (Bolivarian Republic of)'), ('GQ', 'Equatorial Guinea'), ('IM', 'Isle of Man'), ('FK', 'Falkland Islands  [Malvinas]'), ('SJ', 'Svalbard and Jan Mayen'), ('NL', 'Netherlands'), ('BL', 'Saint Barthélemy'), ('IR', 'Iran (Islamic Republic of)'), ('EH', 'Western Sahara'), ('ME', 'Montenegro'), ('GF', 'French Guiana'), ('AQ', 'Antarctica'), ('HT', 'Haiti'), ('MY', 'Malaysia'), ('BD', 'Bangladesh'), ('CH', 'Switzerland'), ('NO', 'Norway'), ('KY', 'Cayman Islands'), ('KH', 'Cambodia'), ('GE', 'Georgia'), ('GT', 'Guatemala'), ('IE', 'Ireland'), ('PH', 'Philippines'), ('NG', 'Nigeria'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('SD', 'Sudan'), ('BJ', 'Benin'), ('CR', 'Costa Rica'), ('EC', 'Ecuador'), ('WS', 'Samoa'), ('PR', 'Puerto Rico'), ('SX', 'Sint Maarten (Dutch part)'), ('CM', 'Cameroon'), ('LR', 'Liberia'), ('KR', 'Korea (the Republic of)'), ('NZ', 'New Zealand'), ('BZ', 'Belize'), ('AZ', 'Azerbaijan'), ('EG', 'Egypt'), ('ST', 'Sao Tome and Principe'), ('DO', 'Dominican Republic'), ('MM', 'Myanmar'), ('PW', 'Palau'), ('HU', 'Hungary'), ('GP', 'Guadeloupe'), ('MD', 'Moldova (the Republic of)'), ('TM', 'Turkmenistan'), ('SV', 'El Salvador'), ('CK', 'Cook Islands'), ('TO', 'Tonga'), ('AX', 'Åland Islands'), ('SA', 'Saudi Arabia'), ('TV', 'Tuvalu'), ('GR', 'Greece'), ('BR', 'Brazil'), ('MO', 'Macao'), ('FM', 'Micronesia (Federated States of)'), ('EE', 'Estonia'), ('SS', 'South Sudan'), ('JE', 'Jersey'), ('ML', 'Mali'), ('AG', 'Antigua and Barbuda'), ('GH', 'Ghana'), ('TL', 'Timor-Leste'), ('AM', 'Armenia'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('WF', 'Wallis and Futuna'), ('LS', 'Lesotho'), ('MT', 'Malta'), ('TH', 'Thailand'), ('JO', 'Jordan'), ('AI', 'Anguilla'), ('FR', 'France'), ('KI', 'Kiribati'), ('CO', 'Colombia'), ('LB', 'Lebanon'), ('KE', 'Kenya'), ('BG', 'Bulgaria'), ('AD', 'Andorra'), ('PN', 'Pitcairn'), ('TG', 'Togo'), ('RE', 'Réunion'), ('BA', 'Bosnia and Herzegovina'), ('GW', 'Guinea-Bissau'), ('OM', 'Oman'), ('KP', "Korea (the Democratic People's Republic of)"), ('MZ', 'Mozambique'), ('SB', 'Solomon Islands'), ('AE', 'United Arab Emirates'), ('LC', 'Saint Lucia'), ('LY', 'Libya'), ('MS', 'Montserrat'), ('MV', 'Maldives'), ('VU', 'Vanuatu'), ('DM', 'Dominica'), ('LU', 'Luxembourg'), ('MP', 'Northern Mariana Islands'), ('SI', 'Slovenia'), ('PA', 'Panama'), ('PT', 'Portugal'), ('NI', 'Nicaragua'), ('GG', 'Guernsey'), ('MC', 'Monaco'), ('VA', 'Holy See'), ('PG', 'Papua New Guinea'), ('GB', 'United Kingdom of Great Britain and Northern Ireland'), ('AW', 'Aruba'), ('BF', 'Burkina Faso'), ('CV', 'Cabo Verde'), ('AR', 'Argentina'), ('MH', 'Marshall Islands'), ('DK', 'Denmark'), ('QA', 'Qatar'), ('VG', 'Virgin Islands (British)'), ('AF', 'Afghanistan')], blank=True, db_index=True, verbose_name='Country', max_length=2)),
                ('harm', models.SmallIntegerField(db_index=True, verbose_name='Harm', default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)])),
                ('blocked', models.BooleanField(db_index=True, verbose_name='Blocked', default=False)),
                ('updated', models.DateTimeField(verbose_name='Updated', default=datetime.datetime(1970, 1, 1, 0, 0))),
                ('dynamic', models.NullBooleanField(verbose_name='Dynamic', default=None)),
                ('city_name', models.CharField(blank=True, verbose_name='City name', max_length=96)),
            ],
            options={
                'verbose_name_plural': 'IP',
                'verbose_name': 'IP',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('path', models.CharField(unique=True, db_index=True, verbose_name='Path', max_length=192)),
            ],
            options={
                'verbose_name_plural': 'site pages',
                'verbose_name': 'site page',
            },
        ),
        migrations.CreateModel(
            name='UserIP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('time', models.PositiveIntegerField(db_index=True, verbose_name='Timestamp', default=scoop.core.util.data.dateutil.now, editable=False)),
                ('ip', models.ForeignKey(to='access.IP', verbose_name='IP', editable=False)),
            ],
            options={
                'verbose_name_plural': 'user IPs',
                'verbose_name': 'user IP',
            },
        ),
    ]
