# coding: utf-8
from __future__ import absolute_import

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.template.defaultfilters import escape
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.shortcuts import addattr


class AuthoredModel(models.Model):
    """ Mixin de modèle ayant un auteur """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, verbose_name=_("Author"))

    # Métadonnées
    class Meta:
        abstract = True


class AuthoredModelAdmin(admin.ModelAdmin):
    """ Mixin d'admin pour les modèles ayant un auteur """

    @addattr(allow_tags=True, admin_order_field='author__username', short_description=_("Author"))
    def get_author_link(self, obj):
        """ Renvoyer un lien vers l'auteur """
        return '<a href="%s">%s</a>' % (obj.author.get_admin_url(), escape(obj.author))


class UseredModelAdmin(admin.ModelAdmin):
    """ Mixin d'admin pour les modèles liés à un utilisateur """

    @addattr(allow_tags=True, admin_order_field='user__username', short_description=_("User"))
    def get_user_link(self, obj):
        """ Renvoyer un lien vers l'utilisateur """
        return '<a href="%s">%s</a>' % (obj.user.get_admin_url(), escape(obj.user))


class AutoAuthoredModelAdmin(admin.ModelAdmin):
    """ Mixin d'admin pour appliquer automatiquement un auteur en cas d'absence """

    # Overrides
    def save_model(self, request, obj, form, change):
        """ Enregistrer l'objet en base de données """
        if obj.author is None:
            obj.author = request.user
        super(AutoAuthoredModelAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """ Sauvegarder le formset """
        if hasattr(formset.model, 'author'):
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.author is None:
                    instance.author = request.user
        super(AutoAuthoredModelAdmin, self).save_formset(request, form, formset, change)

    def get_readonly_fields(self, request, obj=None):
        """ Renvoyer les champs non éditables """
        try:
            field = [f for f in obj._meta.fields if f.name == 'author']
            if len(field) > 0:
                field = field[0]
                field.help_text = _("Automatically set to {name} if let empty").format(name=request.user.username)
        except:
            pass
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        """ Renvoyer le formulaire d'édition """
        form = super(AutoAuthoredModelAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['author'].initial = request.user.id
        try:
            if obj is not None and obj.author is not None:
                form.base_fields['author'].queryset = form.base_fields['author'].queryset.filter(models.Q(id=request.user.id) | models.Q(id=obj.author.id))
            else:
                form.base_fields['author'].queryset = form.base_fields['author'].queryset.filter(id=request.user.id)
        except:
            pass
        return form


class AutoManyAuthoredModelAdmin(admin.ModelAdmin):
    """ Mixin d'admin pour appliquer automatiquement un auteur s'il n'y en a aucun """

    # Overrides
    def save_model(self, request, obj, form, change):
        """ Enregistrer l'objet dans la base de données """
        super(AutoManyAuthoredModelAdmin, self).save_model(request, obj, form, change)
        if not obj.authors.count():
            obj.authors.add(request.user)

    def save_formset(self, request, form, formset, change):
        """ Enregistrer le formset """
        if hasattr(formset.model, 'authors'):
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.authors.count():
                    instance.authors.add(request.user)
        super(AutoManyAuthoredModelAdmin, self).save_formset(request, form, formset, change)

    def get_readonly_fields(self, request, obj=None):
        """ Renvoyer les champs en lecture seule """
        try:
            field = [f for f in obj._meta.fields if f.name == 'authors']
            if len(field) > 0:
                field = field[0]
                field.help_text = _("Automatically set to {name} if let empty").format(name=request.user.username)
        except:
            pass
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        """ Renvoyer le formulaire d'édition """
        form = super(AutoManyAuthoredModelAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['authors'].initial = request.user.id
        try:
            if obj is not None and obj.authors.count() > 0:
                form.base_fields['authors'].queryset = form.base_fields['authors'].queryset.filter(models.Q(id=request.user.id) | models.Q(id=obj.authors.all()[0].id))
            else:
                form.base_fields['authors'].queryset = form.base_fields['authors'].queryset.filter(id=request.user.id)
        except:
            pass
        return form
