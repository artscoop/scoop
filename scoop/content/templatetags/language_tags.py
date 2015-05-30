# coding: utf-8
from __future__ import absolute_import
import re

from classytags.core import Tag, Options
from django import template
from django.utils.translation import pgettext_lazy


register = template.Library()

BASIC_CHANGES = {
    'fr': {u"à le": u"au", u"de le": u"du", u"à les": u"aux", u"de les": u"des"},
}
COUNTRY_IN = {
    'fr': {'ma': u"au", u"mu": u"à", u"re": u"à la", u"mg": u"à"}
}


class Language(Tag):
    """ Tag remplaçant les erreurs de langage, ex. « de le » devient « du » """
    name = 'language'
    options = Options(
        blocks=[('endlanguage', 'nodelist')],
    )

    def render_tag(self, context, **kwargs):
        nodelist = kwargs.get('nodelist', None)
        output = nodelist.render(context)
        # Modifier la sortie
        language = context.get('LANGUAGE_CODE', 'en')
        if language in BASIC_CHANGES:
            for key in BASIC_CHANGES[language]:
                output = re.sub(key, BASIC_CHANGES[language][key], output, flags=re.I)
        return output


register.tag(Language)


@register.simple_tag(takes_context=True)
def in_country(context, country):
    """
    Renvoyer une chaîne de type « dans Pays »
    :type country: scoop.location.models.Country
    """
    language = context.get('LANGUAGE_CODE', 'en')
    if language in COUNTRY_IN and country.code2.lower() in COUNTRY_IN[language]:
        return pgettext_lazy('country_in', u"{adverb} {country}").format(adverb=COUNTRY_IN[language][country.code2.lower()], country=country)
    return pgettext_lazy('country_in', u"in {country}").format(country=country)
