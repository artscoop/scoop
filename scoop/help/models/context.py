# coding: utf-8
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.uuid import UUID64Model


class ContextHelpQuerySet(models.QuerySet):
    """ Manager des aides contextuelles """

    # Getter
    def for_identifier(self, identifier):
        """ Renvoie les éléments d'aide contextuelle pour un nom de contexte """
        names = [name.lower().strip()[len(ContextHelp.HELP_MARKER):] for name in identifier.split() if name.startswith(ContextHelp.HELP_MARKER)]
        return self.filter(name__in=names)

    def for_language(self, language=None):
        """ Renvoie les éléments d'aide contextuelle pour la langue (code 2) """
        language = language or ContextHelp.LANGUAGE
        return self.filter(language=language)

    def active(self):
        """ Renvoyer les aides contextuelles actives """
        return self.filter(active=True)


class ContextHelp(UUID64Model, DatetimeModel):
    """
    Contenu d'aide contextuelle

    Les contenus d'aide contextuelle peuvent n'être accessibles qu'à certains rôles,
    peuvent être activés/désactivés via l'administration.
    Les aides contextuelles sont affichées de la manière suivante :
    - Un middleware analyse le contenu de la page.
    - Les éléments du DOM ayant un id commençant par help- sont récupérés
    - La fin de l'identifiant (ex. pour help-select-role → select-role) est récupérée
    - L'objet ContextHelp dont le nom correspond est récupéré
    - Le markup HTML de la bulle contextuelle est injecté.
    """

    # Constantes
    HELP_MARKER = 'ctx-help-'
    LANGUAGES = settings.LANGUAGES
    LANGUAGE = settings.LANGUAGE_CODE
    NAME_HINT = _("Name must be lowercase letters, digits or hyphen, and start with a letter.")

    # Champs
    active = models.BooleanField(default=True, verbose_name="Active")
    language = models.CharField(max_length=5, choices=LANGUAGES, default=LANGUAGE, blank=False, db_index=True, verbose_name=_("Language"))
    name = models.CharField(max_length=64, blank=False, validators=[RegexValidator(r'^[a-z][a-z0-9\-]+$')], help_text=NAME_HINT, verbose_name=_("Name"))
    text = models.TextField(blank=False, verbose_name=_("Text"))
    objects = ContextHelpQuerySet.as_manager()

    # Rendu
    def render(self, request=None):
        if self.is_visible(request):
            output = render_to_string('help/display/context-help.html', {'help': self}, request=request)
            return output
        return None

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation de l'objet """
        return "context help - {0}".format(self.name)

    # Meta
    class Meta:
        verbose_name = _("Context help")
        verbose_name_plural = _("Context help")
        unique_together = [['language', 'name']]
        app_label = 'help'
