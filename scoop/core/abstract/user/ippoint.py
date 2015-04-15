# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from IPy import IP as IP_


class IPPointModel(models.Model):
    """ Mixin de modèle pointant vers une adresse IP """
    ip = models.ForeignKey('access.IP', editable=False, verbose_name=_(u"IP"))

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
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _(u"{}").format(self.get_ip())

    # Propriétés
    ip_address = property(get_ip, set_ip)

    # Métadonnées
    class Meta:
        abstract = True


class IPPointableModel(models.Model):
    """ Mixin de modèle pouvant pointer vers une IP """
    # Champs
    ip = models.ForeignKey('access.IP', db_index=True, null=True, on_delete=models.SET_NULL, verbose_name=_(u"IP"))

    # Getter
    def get_ip(self):
        """ Renvoyer l'objet IP lié, ou None """
        return self.ip

    def get_ip_address(self):
        """ Renvoyer l'adresse IP au format A.B.C.D ou une chaîne vide """
        return IP_(self.ip).strNormal() if self.ip else ""

    # Setter
    def set_ip(self, ip):
        """
        Définir une IP pour l'objet
        :param ip: adresse ip sous la forme A.B.C.D
        """
        from scoop.user.access.models.ip import IP
        # Ne pas sauvegarder automatiquement la modification
        self.ip = IP.objects.get_by_ip(ip)

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _(u"{}").format(self.get_ip())

    # Propriétés
    ip_address = property(get_ip, set_ip)

    # Métadonnées
    class Meta:
        abstract = True
