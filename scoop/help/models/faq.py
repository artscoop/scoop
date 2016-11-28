# coding: utf-8

from markdown import markdown

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.util.shortcuts import addattr
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, TranslatableModelManager, get_translation_model


class FAQQuerySet(models.QuerySet, TranslatableModelManager):
    """ Manager des questions de la FAQ """

    # Getter
    def by_group(self, name):
        """ Renvoyer les FAQ appartenant à un groupe """
        return self.filter(groups__name__iexact=name)

    def active(self):
        """ Rnevoyer les FAQ actives """
        return self.filter(active=True)


class FAQ(DatetimeModel, UUID64Model, WeightedModel, TranslatableModel):
    """ Question fréquemment posée """

    # Constantes
    FORMATTING = [[0, _("HTML")], [1, _("Markdown")]]

    # Champs
    active = models.BooleanField(default=True, verbose_name=pgettext_lazy('faq', "Active"))
    groups = models.ManyToManyField('help.helpgroup', blank=True, verbose_name=_("Groups"))
    format = models.SmallIntegerField(default=0, choices=FORMATTING, verbose_name=_("Format"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('faq', "Updated"))
    objects = FAQQuerySet.as_manager()

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
    answer = cached_property(get_answer, name='answer')
    question = cached_property(get_question, name='question')

    # Overrides
    def __str__(self):
        """ Renvoyer la représentation de l'objet """
        return "FAQ - {0}".format(self.uuid)

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
