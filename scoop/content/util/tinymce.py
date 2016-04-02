# coding: utf-8
from django.conf import settings


TINYMCE_CONFIG_CONTENT = {'menubar': False, 'statusbar': False,
                          'toolbar': 'undo redo | styleselect | bold italic underline | link | bullist | code',
                          'plugins': 'code link autolink preview autoresize',
                          'skin': 'lightgray', 'body_class': 'texted',
                          'content_css': "{0}tool/tinymce/editor.css".format(settings.STATIC_URL),
                          'autoresize_max_height': 320, 'autoresize_min_height': 24}
