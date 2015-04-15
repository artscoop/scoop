# coding: utf-8

# Liste de correspondance code langue vers code pays
LANGUAGE_COUNTRY = {'en': 'gb'}


def get_country_code(language):
    """ Renvoyer un code pays par rapport à une langue """
    language = language.lower()
    return LANGUAGE_COUNTRY.get(language, language)
