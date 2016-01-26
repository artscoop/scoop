# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy


class CreationLicenseModel(models.Model):
    """ Objet possédant une information de licence """

    # Constantes
    LICENSES = {0: pgettext_lazy('audience', 'None'), 1: 'Copyright', 10: 'CC-BY', 11: 'CC-BY-SA', 12: 'CC-BY-ND', 13: 'CC-BY-NC', 14: 'CC-BY-SA-NC', 15: 'CC-BY-ND-ND', 16: 'Public domain'}
    LICENSE_SEPARATOR = ';'

    # Champs
    license = models.CharField(max_length=40, default=";", blank=True, verbose_name=_("License/Creator"))

    # Getter
    def get_license_id(self):
        """ Renvoyer l'id de la licence """
        licens, _ = self.license.split(self.LICENSE_SEPARATOR, 1)
        return int(licens or 0)

    def get_license_name(self):
        """ Renvoyer le nom de la licence """
        return self.LICENSES[self.get_license_id()]

    def get_license_creator(self):
        """ Renvoyer le nom de l'auteur """
        _, creator = self.license.split(self.LICENSE_SEPARATOR, 1)
        return creator or _("Not provided")

    # Métadonnées
    class Meta:
        abstract = True


class AudienceModel(models.Model):
    """ Objet indiquant le type de public approprié à son visionnage """

    # Constantes
    AUDIENCES = {0: _("Everyone"), 5: _("Adults only")}
    AUDIENCE_AGES = {0: 3, 5: 18}
    AUDIENCE_CHOICES = AUDIENCES.items()

    # Champs
    audience = models.SmallIntegerField(choices=AUDIENCE_CHOICES, default=0, verbose_name=_("Audience rating"))

    # Getter
    def get_audience_minimal_age(self):
        """ Renvoyer l'âge minimal pour accéder à ce contenu """
        return self.AUDIENCE_AGES.get(self.audience, 0)

    # Métadonnées
    class Meta:
        abstract = True
