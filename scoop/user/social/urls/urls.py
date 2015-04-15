# coding: utf-8
""" URLs de l'application Utilisateurs """
from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'^ask/(?P<uid>\d+)$', 'social.views.page.add_friend', name='page-add-friend'),
                       )
