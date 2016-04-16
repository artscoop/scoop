# coding: utf-8
from IPy import IP as IP_
from django.apps.registry import apps
from django.db import models
from django.utils.translation import ugettext_lazy as _


class IPPointMixin():
    """ Mixin de méthodes pour les modèles pointant vers une adresse IP """
    if apps.is_installed('scoop.user.access'):
        # Getter
        def get_ip(self):
            """ Renvoyer l'objet IP lié """
            return self.ip

        def get_ip_address(self):
            """ Renvoyer l'adresse IP au format A.B.C.D """
            return IP_(self.ip).strNormal()

        # Setter
        def set_ip(self, ip):
            """
            Définir une IP pour l'objet
            :param ip: ip de la forme A.B.C.D
            """
            from scoop.user.access.models.ip import IP
            # Ne pas sauvegarder automatiquement la modification
            self.ip = IP.objects.get_by_ip(ip)

        # Overrides
        def __str__(self):
            """ Renvoyer la représentation unicode de l'objet """
            return _("{}").format(self.get_ip())

        # Propriétés
        ip_address = property(get_ip, set_ip)


class IPPointModel(models.Model, IPPointMixin):
    """ Mixin de modèle pointant vers une adresse IP """
    if apps.is_installed('scoop.user.access'):
        ip = models.ForeignKey('access.IP', editable=False, verbose_name=_("IP"))

    # Métadonnées
    class Meta:
        abstract = True


class IPPointableModel(models.Model, IPPointMixin):
    """ Mixin de modèle pouvant pointer vers une IP """
    if apps.is_installed('scoop.user.access'):
        ip = models.ForeignKey('access.IP', db_index=True, blank=True, null=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_("IP"))

    # Métadonnées
    class Meta:
        abstract = True
