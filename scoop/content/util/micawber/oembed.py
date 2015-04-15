# coding: utf-8


def bootstrap_oembed(cache=None):
    """ Ajouter des fournisseurs oEmbed à la liste par défaut de Micawber """
    from micawber.contrib.mcdjango.providers import bootstrap_basic
    from micawber.providers import Provider
    # Ajouter au registre
    registry = bootstrap_basic()
    registry.register('http://\S*?dailymotion.com/\S*', Provider('http://www.dailymotion.com/services/oembed/'))
    return registry
