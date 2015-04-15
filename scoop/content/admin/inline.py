# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline
from django.db import models
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _

from scoop.content.forms.picture import PictureAdminInlineForm
from scoop.content.models.content import Category, CategoryTranslation
from scoop.content.models.picture import Picture
from scoop.content.util.widgets import PictureInlineWidget


class PictureInlineAdmin(GenericTabularInline):
    """ Inline admin des images """
    model = Picture
    form = PictureAdminInlineForm
    ordering = ['weight']
    max_num = 8
    formfield_overrides = {models.ImageField: {'widget': PictureInlineWidget}, models.TextField: {'widget': widgets.Input(attrs={'maxlength': 1024})}}


class CategoryInline(admin.TabularInline):
    """ Inline admin des types de contenus """
    model = Category


class CategoryTranslationInlineAdmin(admin.TabularInline):
    """ Inline admin des traductions de contenu """
    verbose_name = _(u"Translation")
    verbose_name_plural = _(u"Translations")
    model = CategoryTranslation
    max_num = len(settings.LANGUAGES)
    formfield_overrides = {models.TextField: {'widget': admin.widgets.AdminTextInputWidget}, }
    extra = 1
