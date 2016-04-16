# coding: utf-8
import re

from classytags.core import Options, Tag
from django import template
from django.utils.translation import pgettext_lazy


register = template.Library()

BASIC_CHANGES = {
    'fr': {"à le": "au", "de le": "du", "à les": "aux", "de les": "des"},
}
COUNTRY_IN = {
    'fr': {'ma': "au", "mu": "à", "re": "à la", "mg": "à"}
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
        return pgettext_lazy('country_in', "{adverb} {country}").format(adverb=COUNTRY_IN[language][country.code2.lower()], country=country)
    return pgettext_lazy('country_in', "in {country}").format(country=country)
