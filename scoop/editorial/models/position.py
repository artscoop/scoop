# coding: utf-8
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.http.request import HttpRequest
from django.template.defaultfilters import capfirst
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.icon import IconModel

# Positions à traduire par défaut
DEFAULT_NAMES = [_("Menu"), _("Heading"), _("Footer"), _("Js"), _("Extra head"), ]


class Position(DatetimeModel, IconModel):
    """ Emplacement dans un template """

    # Champs
    name = models.SlugField(max_length=64, unique=True, blank=False, help_text=_("Name used for the position block in a template"), verbose_name=_("Name"))
    title = models.CharField(max_length=64, blank=False, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    # Accès
    anonymous = models.BooleanField(default=True, blank=True, verbose_name=_("Anonymous access"))
    authenticated = models.BooleanField(default=True, blank=True, verbose_name=_("Authenticated access"))
    groups = models.ManyToManyField('auth.Group', blank=True, verbose_name=_("Access for groups"))

    # Getter
    @staticmethod
    def get(name):
        """ Renvoyer une position par son nom """
        position = Position.objects.get_or_create(name=name.lower())
        if isinstance(position, tuple):
            position = position[0]
        position.auto_title()
        return position

    def has_access(self, user):
        """ Renvoyer si un utilisateur a accès à ce contenu """
        # Si user est une request
        if isinstance(user, (WSGIRequest, HttpRequest)):
            return self.has_access(getattr(user, 'user', AnonymousUser()))
        # Pour les anonymes
        elif user == AnonymousUser or user.is_anonymous():
            return self.anonymous
        # Pour les enregistrés
        elif user.is_authenticated() and self.authenticated:
            return True
        # Pour les enregistrés de certains groupes
        elif hasattr(user, 'pk') and self.groups.filter(user=user).exists():
            return True
        return False

    # Setter
    def auto_title(self):
        """ Définir un titre automatique à partir du nom """
        if not self.title:
            self.title = capfirst(self.name.replace('_', ' '))
            self.save()
        return self.title

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return ugettext(self.auto_title())

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super(Position, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("position")
        verbose_name_plural = _("positions")
        app_label = 'editorial'
