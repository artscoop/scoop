# coding: utf-8
from django.dispatch.dispatcher import Signal


analyzer_default_format = Signal(providing_args=['value', 'category'])
