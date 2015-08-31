# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.contrib.gis.db.models.fields
import scoop.core.util.data.dateutil
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Access',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('referrer', models.CharField(max_length=192, verbose_name='Referrer')),
            ],
            options={
                'verbose_name': 'access',
                'verbose_name_plural': 'accesses',
            },
        ),
        migrations.CreateModel(
            name='IP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('position', django.contrib.gis.db.models.fields.PointField(default=(0.0, 0.0), srid=4326)),
                ('ip', models.DecimalField(decimal_places=0, max_digits=39, blank=True, unique=True, verbose_name='Decimal', db_index=True)),
                ('string', models.CharField(max_length=48, verbose_name='String')),
                ('reverse', models.CharField(max_length=80, verbose_name='Reverse', blank=True)),
                ('status', models.SmallIntegerField(default=0, verbose_name='Reverse status', choices=[[0, 'Ok'], [1, 'Timed out'], [2, 'Empty answer'], [3, 'Broken NS'], [4, 'Domain not found']])),
                ('isp', models.CharField(max_length=64, verbose_name='ISP', blank=True)),
                ('country', models.CharField(blank=True, max_length=2, verbose_name='Country', db_index=True, choices=[('WF', 'Wallis and Futuna'), ('JP', 'Japan'), ('JM', 'Jamaica'), ('JO', 'Jordan'), ('WS', 'Samoa'), ('JE', 'Jersey'), ('GW', 'Guinea-Bissau'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GS', 'South Georgia and the South Sandwich Islands'), ('GR', 'Greece'), ('GQ', 'Equatorial Guinea'), ('GP', 'Guadeloupe'), ('GY', 'Guyana'), ('GG', 'Guernsey'), ('GF', 'French Guiana'), ('GE', 'Georgia'), ('GD', 'Grenada'), ('GB', 'United Kingdom of Great Britain and Northern Ireland'), ('GA', 'Gabon'), ('GN', 'Guinea'), ('GM', 'Gambia'), ('GL', 'Greenland'), ('GI', 'Gibraltar'), ('GH', 'Ghana'), ('PR', 'Puerto Rico'), ('PS', 'Palestine, State of'), ('PW', 'Palau'), ('PT', 'Portugal'), ('PY', 'Paraguay'), ('PA', 'Panama'), ('PF', 'French Polynesia'), ('PG', 'Papua New Guinea'), ('PE', 'Peru'), ('PK', 'Pakistan'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PM', 'Saint Pierre and Miquelon'), ('ZM', 'Zambia'), ('ZA', 'South Africa'), ('ZW', 'Zimbabwe'), ('ME', 'Montenegro'), ('MD', 'Moldova (the Republic of)'), ('MG', 'Madagascar'), ('MF', 'Saint Martin (French part)'), ('MA', 'Morocco'), ('MC', 'Monaco'), ('MM', 'Myanmar'), ('ML', 'Mali'), ('MO', 'Macao'), ('MN', 'Mongolia'), ('MH', 'Marshall Islands'), ('MK', 'Macedonia (the former Yugoslav Republic of)'), ('MU', 'Mauritius'), ('MT', 'Malta'), ('MW', 'Malawi'), ('MV', 'Maldives'), ('MQ', 'Martinique'), ('MP', 'Northern Mariana Islands'), ('MS', 'Montserrat'), ('MR', 'Mauritania'), ('MY', 'Malaysia'), ('MX', 'Mexico'), ('MZ', 'Mozambique'), ('FR', 'France'), ('FI', 'Finland'), ('FJ', 'Fiji'), ('FK', 'Falkland Islands  [Malvinas]'), ('FM', 'Micronesia (Federated States of)'), ('FO', 'Faroe Islands'), ('CK', 'Cook Islands'), ('CI', "C\xf4te d'Ivoire"), ('CH', 'Switzerland'), ('CO', 'Colombia'), ('CN', 'China'), ('CM', 'Cameroon'), ('CL', 'Chile'), ('CC', 'Cocos (Keeling) Islands'), ('CA', 'Canada'), ('CG', 'Congo'), ('CF', 'Central African Republic'), ('CD', 'Congo (the Democratic Republic of the)'), ('CZ', 'Czech Republic'), ('CY', 'Cyprus'), ('CX', 'Christmas Island'), ('CR', 'Costa Rica'), ('CW', 'Cura\xe7ao'), ('CV', 'Cabo Verde'), ('CU', 'Cuba'), ('SZ', 'Swaziland'), ('SY', 'Syrian Arab Republic'), ('SX', 'Sint Maarten (Dutch part)'), ('SS', 'South Sudan'), ('SR', 'Suriname'), ('SV', 'El Salvador'), ('ST', 'Sao Tome and Principe'), ('SK', 'Slovakia'), ('SJ', 'Svalbard and Jan Mayen'), ('SI', 'Slovenia'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('SO', 'Somalia'), ('SN', 'Senegal'), ('SM', 'San Marino'), ('SL', 'Sierra Leone'), ('SC', 'Seychelles'), ('SB', 'Solomon Islands'), ('SA', 'Saudi Arabia'), ('SG', 'Singapore'), ('SE', 'Sweden'), ('SD', 'Sudan'), ('YE', 'Yemen'), ('YT', 'Mayotte'), ('LB', 'Lebanon'), ('LC', 'Saint Lucia'), ('LA', "Lao People's Democratic Republic"), ('LK', 'Sri Lanka'), ('LI', 'Liechtenstein'), ('LV', 'Latvia'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('LR', 'Liberia'), ('LS', 'Lesotho'), ('LY', 'Libya'), ('VA', 'Holy See'), ('VC', 'Saint Vincent and the Grenadines'), ('VE', 'Venezuela (Bolivarian Republic of)'), ('VG', 'Virgin Islands (British)'), ('IQ', 'Iraq'), ('VI', 'Virgin Islands (U.S.)'), ('IS', 'Iceland'), ('IR', 'Iran (Islamic Republic of)'), ('IT', 'Italy'), ('VN', 'Viet Nam'), ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IO', 'British Indian Ocean Territory'), ('IN', 'India'), ('IE', 'Ireland'), ('ID', 'Indonesia'), ('BD', 'Bangladesh'), ('BE', 'Belgium'), ('BF', 'Burkina Faso'), ('BG', 'Bulgaria'), ('BA', 'Bosnia and Herzegovina'), ('BB', 'Barbados'), ('BL', 'Saint Barth\xe9lemy'), ('BM', 'Bermuda'), ('BN', 'Brunei Darussalam'), ('BO', 'Bolivia (Plurinational State of)'), ('BH', 'Bahrain'), ('BI', 'Burundi'), ('BJ', 'Benin'), ('BT', 'Bhutan'), ('BV', 'Bouvet Island'), ('BW', 'Botswana'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('BR', 'Brazil'), ('BS', 'Bahamas'), ('BY', 'Belarus'), ('BZ', 'Belize'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('RS', 'Serbia'), ('RE', 'R\xe9union'), ('RO', 'Romania'), ('OM', 'Oman'), ('HR', 'Croatia'), ('HT', 'Haiti'), ('HU', 'Hungary'), ('HK', 'Hong Kong'), ('HN', 'Honduras'), ('HM', 'Heard Island and McDonald Islands'), ('EH', 'Western Sahara'), ('EE', 'Estonia'), ('EG', 'Egypt'), ('EC', 'Ecuador'), ('ET', 'Ethiopia'), ('ES', 'Spain'), ('ER', 'Eritrea'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('US', 'United States of America'), ('UM', 'United States Minor Outlying Islands'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('VU', 'Vanuatu'), ('NI', 'Nicaragua'), ('NL', 'Netherlands'), ('NO', 'Norway'), ('NA', 'Namibia'), ('NC', 'New Caledonia'), ('NE', 'Niger'), ('NF', 'Norfolk Island'), ('NG', 'Nigeria'), ('NZ', 'New Zealand'), ('NP', 'Nepal'), ('NR', 'Nauru'), ('NU', 'Niue'), ('KG', 'Kyrgyzstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KH', 'Cambodia'), ('KN', 'Saint Kitts and Nevis'), ('KM', 'Comoros'), ('KR', 'Korea (the Republic of)'), ('KP', "Korea (the Democratic People's Republic of)"), ('KW', 'Kuwait'), ('KZ', 'Kazakhstan'), ('KY', 'Cayman Islands'), ('DO', 'Dominican Republic'), ('DM', 'Dominica'), ('DJ', 'Djibouti'), ('DK', 'Denmark'), ('DE', 'Germany'), ('DZ', 'Algeria'), ('TZ', 'Tanzania, United Republic of'), ('TV', 'Tuvalu'), ('TW', 'Taiwan (Province of China)'), ('TT', 'Trinidad and Tobago'), ('TR', 'Turkey'), ('TN', 'Tunisia'), ('TO', 'Tonga'), ('TL', 'Timor-Leste'), ('TM', 'Turkmenistan'), ('TJ', 'Tajikistan'), ('TK', 'Tokelau'), ('TH', 'Thailand'), ('TF', 'French Southern Territories'), ('TG', 'Togo'), ('TD', 'Chad'), ('TC', 'Turks and Caicos Islands'), ('AE', 'United Arab Emirates'), ('AD', 'Andorra'), ('AG', 'Antigua and Barbuda'), ('AF', 'Afghanistan'), ('AI', 'Anguilla'), ('AM', 'Armenia'), ('AL', 'Albania'), ('AO', 'Angola'), ('AQ', 'Antarctica'), ('AS', 'American Samoa'), ('AR', 'Argentina'), ('AU', 'Australia'), ('AT', 'Austria'), ('AW', 'Aruba'), ('AX', '\xc5land Islands'), ('AZ', 'Azerbaijan'), ('QA', 'Qatar')])),
                ('harm', models.SmallIntegerField(default=0, db_index=True, verbose_name='Harm', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)])),
                ('blocked', models.BooleanField(default=False, db_index=True, verbose_name='Blocked')),
                ('updated', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), verbose_name='Updated')),
                ('dynamic', models.NullBooleanField(default=None, verbose_name='Dynamic')),
                ('city_name', models.CharField(max_length=96, verbose_name='City name', blank=True)),
            ],
            options={
                'verbose_name': 'IP',
                'verbose_name_plural': 'IP',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.CharField(unique=True, max_length=192, verbose_name='Path', db_index=True)),
            ],
            options={
                'verbose_name': 'site page',
                'verbose_name_plural': 'site pages',
            },
        ),
        migrations.CreateModel(
            name='UserIP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.PositiveIntegerField(default=scoop.core.util.data.dateutil.now, verbose_name='Timestamp', editable=False, db_index=True)),
                ('ip', models.ForeignKey(editable=False, to='access.IP', verbose_name='IP')),
            ],
            options={
                'verbose_name': 'user IP',
                'verbose_name_plural': 'user IPs',
            },
        ),
    ]
