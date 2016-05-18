# coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from markdown import markdown
from translatable.exceptions import MissingTranslation
from translatable.models import get_translation_model

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.util.shortcuts import addattr


class FAQManager(models.Manager):
    """ Manager des questions de la FAQ """

    # Getter
    def by_group(self, name):
        """ Renvoyer les FAQ appartenant à un groupe """
        return self.filter(group=name)


class FAQ(DatetimeModel, UUID64Model):
    """ Question fréquemment posée """

    # Constantes
    FORMATTING = [[0, _("HTML")], [1, _("Markdown")]]

    # Champs
    active = models.BooleanField(default=True, verbose_name=pgettext_lazy('faq', "Active"))
    group = models.CharField(max_length=64, blank=True, verbose_name=_("Group"))
    format = models.SmallIntegerField(default=0, choices=FORMATTING, verbose_name=_("Format"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('faq', "Updated"))
    objects = FAQManager()

    # Getter
    def get_answer_html(self):
        """ Effectuer le rendu HTML de la réponse """
        formatting = {0: lambda x: x, 1: lambda x: markdown(x)}
        return formatting[self.format](self.answer)

    # Getter
    @addattr(short_description=_("Answer"))
    def get_answer(self):
        """ Renvoyer la description de l'option """
        try:
            return self.get_translation().answer
        except MissingTranslation:
            return _("(No text)")

    @addattr(short_description=_("Question"))
    def get_question(self):
        """ Renvoyer la question """
        try:
            return self.get_translation().question
        except MissingTranslation:
            return _("(No question)")

    # Propriétés
    answer = property(get_answer)
    question = property(get_question)

    # Méta
    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")
        app_label = 'help'


class FAQTranslation(get_translation_model(FAQ, "faq"), TranslationModel):
    """ Traduction des pages """

    # Champs
    question = models.CharField(max_length=240, blank=False, verbose_name=_("Question"))
    answer = models.TextField(blank=False, verbose_name=_("Text"))

    # Métadonnées
    class Meta:
        app_label = 'help'
