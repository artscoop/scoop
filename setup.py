#!/usr/bin/env python
# coding: utf-8
from distutils.core import setup

from setuptools import find_packages

setup(
    name='scoop',
    version='0.10.20160611',
    packages=find_packages('.'),
    include_package_data=True,
    url='',
    license='',
    author='Steve Kossouho',
    author_email='steve.kossouho@gmail.com',
    description='The django scoop project by artscoop',
    requires=['django', 'bleach', 'beautifulsoup4', 'bpython', 'coverage', 'django_autoslug', 'django_celery', 'django_jsonresponse', 'django_reversion',
              'django_simple_captcha', 'django_translatable', 'dj_cmd', 'dnspython3', 'fuzzywuzzy', 'gunicorn', 'html5lib', 'ipy', 'ipython', 'isort',
              'loremipsum', 'lxml', 'markdown', 'micawber', 'mysqlclient', 'ngram', 'nltk', 'numpy', 'paramiko', 'pexpect', 'pillow', 'psycopg2', 'pyproj',
              'python_levenshtein', 'python_dateutil', 'python_magic', 'pytz', 'rarfile', 'requests', 'simplejson', 'textblob', 'unicodecsv', 'unidecode'],
    dependency_links=['https://bitbucket.org/ubernostrum/webcolors/get/default.zip',
                      'https://github.com/giampaolo/psutil/archive/master.zip',
                      'https://github.com/coleifer/micawber/archive/master.zip',
                      'https://github.com/SmileyChris/easy-thumbnails/archive/master.zip',
                      'https://github.com/jsocol/django-waffle/archive/master.zip',
                      'https://bitbucket.org/basaundi/django-languages/get/default.zip',
                      'https://github.com/blturner/django_inlines/archive/master.zip',
                      'https://github.com/alex/django-filter/archive/develop.zip',
                      'https://github.com/django-extensions/django-extensions/archive/master.zip',
                      'https://github.com/artscoop/django-disposable-email-checker/archive/master.zip',
                      'https://bitbucket.org/mjs7231/django-dbbackup/get/default.zip',
                      'https://github.com/SmileyChris/django-countries/archive/master.zip',
                      ]
)
