# coding: utf-8
import re

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language, pgettext_lazy
from django_languages.fields import LanguageField
from scoop.core.util.model.model import SingleDeleteManager
from scoop.rogue.templatetags.profanity_tags import ProfanitiesFilter


class ProfanityManager(SingleDeleteManager):
    """ Manager des filtres de grossièretés """

    # Getter
    def for_text(self, text):
        """ Renvoyer tous les filtres ayant eu un effet sur la chaîne """
        return [profanity for profanity in self.all() if profanity.check_text(text)]


class Profanity(models.Model):
    """ Filtre de grossièretés """

    # Champs
    active = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('profanity.filter', "Active"))
    language = LanguageField(default=get_language(), blank=True, verbose_name=_("Language"))
    regex = models.CharField(max_length=120, unique=True, verbose_name=_("Regex"))
    standalone = models.BooleanField(default=True, null=False, db_index=True, verbose_name=pgettext_lazy('profanity.filter', "Standalone"))
    description = models.TextField(blank=True, default="", verbose_name=_("Description"))
    objects = ProfanityManager()

    # Getter
    def check_text(self, text):
        """ Renvoyer si ce filtre est positif pour une chaîne de caractères """
        return re.search(re.escape(str(self.regex)), text)

    @staticmethod
    def concatenate(standalone=True, language=None):
        """ Concaténer tous les filtres """
        exps = Profanity.objects.filter(active=True, standalone=standalone, language__in=[language or "", ""]).iterator()
        output = "|".join(["({exp})".format(exp=x.regex) for x in exps])
        return output

    @staticmethod
    def process(text):
        """ Renvoyer une chaîne privée de ses grosièretés """
        return ProfanitiesFilter.filter_profanities(text)

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return _("Profanity with pattern {regex}").format(regex=self.regex)

    # Métadonnées
    class Meta:
        verbose_name = _("profanity")
        verbose_name_plural = _("profanities")
        app_label = 'rogue'
        ordering = ['regex']
