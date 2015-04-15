# coding: utf-8
from __future__ import absolute_import

import random
import re

from django.template import Library


register = Library()


class ProfanitiesFilter(object):
    """ Filtre de grossièretés """

    # Overrides
    def __init__(self, filterlist, ignore_case=True, replacements="-", complete=True, inside_words=False):
        """ Initialiser le filtre """
        self.badwords = filterlist
        self.ignore_case = ignore_case
        self.replacements = replacements
        # Remplacer le mot complet ou conserver la première et dernière lettre ?
        self.complete = complete
        # Remplacer les mots contenus dans d'autres ? ex. recul = re---
        self.inside_words = inside_words
        super(ProfanitiesFilter, self).__init__()

    # Actions (Privé)
    def _make_clean_word(self, length):
        """ Nettoyer un mot """
        # Générer une chaîne de n caractères avec self.replacements
        return ''.join([random.choice(self.replacements) for _ in xrange(length)])

    def __replacer(self, match):
        """ Remplacer une correspondance """
        value = match.group()
        if self.complete:
            return self._make_clean_word(len(value))
        else:
            return value[0] + self._make_clean_word(len(value) - 2) + value[-1]

    # Actions
    def clean(self, text):
        """ Nettoyer les grossièretés d'un texte """
        # Changer la regexp selon que le filtre concerne l'intérieur des mots
        regexp_insidewords = {True: r'(%s)', False: r'\b(%s)\b'}
        regexp = (regexp_insidewords[self.inside_words] % '|'.join(self.badwords))
        r = re.compile(regexp, re.IGNORECASE if self.ignore_case else 0)
        # Renvoyer la version nettoyée de la chaîne
        return r.sub(self.__replacer, text)

    # Getter
    @staticmethod
    def filter_profanities(text):
        """ Nettoyer automatiquement les grossièretés """
        from scoop.rogue.models.profanity import Profanity
        # Filtrer séparément les standalone et le reste
        regex1 = Profanity.concatenate(standalone=True)
        regex2 = Profanity.concatenate(standalone=False)
        filter1 = ProfanitiesFilter(regex1, complete=False, inside_words=False)
        filter2 = ProfanitiesFilter(regex2, complete=False, inside_words=True)
        # Renvoyer le contenu filtré par filtre1 et filtre2
        return filter1.clean(filter2.clean(text))


@register.filter(name='clean_profanity')
def clean_profanities(value):
    """ Filtrer les grossièretés du texte """
    return ProfanitiesFilter.filter_profanities(value)
