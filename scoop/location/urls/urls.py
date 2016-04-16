# coding: utf-8
from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       # AJAX Villes
                       url(r'^city/suggest$', 'scoop.location.views.ajax.complete', name='city-ajax-suggest'),
                       # url(r'^city/weather/(?P<city>\d+)$', 'location.views.view.view_city_weather', name='city-weather'),
                       )
