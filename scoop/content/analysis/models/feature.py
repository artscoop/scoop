# coding: utf-8
from __future__ import absolute_import

import nltk
from django.db import models
from django.template.defaultfilters import striptags
from django.utils.translation import ugettext_lazy as _
from nltk.tokenize import word_tokenize

from scoop.core.templatetags.text_tags import truncate_stuckkey


class Feature(models.Model):
    """ Caractéristique d'un document """
    # Constantes
    STATUSES = [[0, _("Word")], [1, _("Number")], [2, _("Email")]]
    # Champs
    name = models.CharField(max_length=32, blank=False, verbose_name=_("Name"))
    status = models.SmallIntegerField(default=0, verbose_name=_("Feature type"))

    # Getter
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return self.name

    # Setter
    @staticmethod
    def get_from_text(document):
        """ Renvoyer les caractéristiques du document """
        def _accept_word(word):
            """ Accepter un mot du document """
            is_word = (2 < len(word) < 27)
            return is_word

        # Traitement
        document = truncate_stuckkey(striptags(document), length=3)
        stopwords = nltk.corpus.stopwords.words('french')
        words = [word.lower() for word in word_tokenize(document) if (_accept_word(word) and word not in stopwords)]
        features = []
        for word in words:
            feature, _ = Feature.objects.get_or_create(name=word)
            features.append(feature)
        return features

    # Métadonnées
    class Meta:
        verbose_name = _("feature")
        verbose_name_plural = _("features")
        app_label = 'analysis'
