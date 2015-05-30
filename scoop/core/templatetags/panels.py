# coding: utf-8
from django.conf import settings
from django.core import urlresolvers
from django.core.exceptions import ViewDoesNotExist
from django.template import Library, Node, TemplateSyntaxError, Variable
from django.utils.translation import ugettext_lazy as _

register = Library()


class ViewNode(Node):
    """
    Insérer le contenu d'une vue Django ou d'une URL dans un template
    Insertion par nom d'url (paramètre name) ou par chemin complet de fonction
    La vue peut renvoyer une HttpReponse ou une chaîne de caractères.
    (Code basé sur un snippet de James G. Pearce, 17 juin 2009)
    """

    def __init__(self, url_or_view, args, kwargs):
        """ Initialiser le nœud """
        self.url_or_view = url_or_view
        self.args = args
        self.kwargs = kwargs

    def render(self, context):
        """ Effectuer le rendu du nœud """
        # Renvoyer chaîne vide si aucune variable request à passer
        if 'request' not in context:
            return ''
        request = context['request']
        url_or_view = Variable(self.url_or_view).resolve(context)
        try:
            urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
            resolver = urlresolvers.RegexURLResolver(r'^/', urlconf)
            kwargs = {key: Variable(value).resolve(context) for (key, value) in self.kwargs.items()}
            url_or_view = urlresolvers.reverse(url_or_view, kwargs=kwargs)
            view, args, kwargs = resolver.resolve(url_or_view)
        except:
            view = urlresolvers.get_callable(url_or_view, True)
            args = [Variable(arg).resolve(context) for arg in self.args]
            kwargs = {key: Variable(value).resolve(context) for key, value in self.kwargs.items()}
        if callable(view):
            output = view(request, *args, **kwargs)
            return getattr(output, 'content', output)
        if settings.TEMPLATE_DEBUG:
            output = (_(u"%(viewname)r is not a method or function and cannot be called") % {'viewname': view})
            raise ViewDoesNotExist(output)
        return ''


class ViewFuncNode(Node):
    """
    Insérer le contenu d'une vue Django ou d'une URL dans un template
    Insertion par chemin complet de fonction
    La vue peut renvoyer une HttpReponse ou une chaîne de caractères.
    (Code basé sur un snippet de James G. Pearce, 17 juin 2009)
    """

    def __init__(self, view, args, kwargs):
        """ Initialiser le nœud """
        self.view = view
        self.args = args
        self.kwargs = kwargs

    def render(self, context):
        """ Effectuer le rendu du nœud """
        # Renvoyer chaîne vide si aucune variable request à passer
        if 'request' in context:
            request = context['request']
            view = urlresolvers.get_callable(Variable(self.view).resolve(context), True)
            args = [Variable(arg).resolve(context) for arg in self.args]
            kwargs = {key: Variable(value).resolve(context) for key, value in self.kwargs.items()}
            if callable(view):
                output = view(request, *args, **kwargs)
                return getattr(output, 'content', output)
            elif settings.TEMPLATE_DEBUG:
                output = _(u"{viewname} is not a method or function and cannot be called").format(viewname=view)
                raise ViewDoesNotExist(output)
        return u""


def do_view(parser, token):
    """
    Afficher le contenu d'une vue, à l'aide de son nom d'URL, nom pleinement
    qualifié de vue ou son URL locale.
    ex. {% view "mymodule.views.inner" [arg_expr] [kwarg=expr] %}
    ex. {% view "/url/to/view" ... %}
    ex. {% view "url_name" (URL args etc.) %}
    IMPORTANT : Le template appelant doit avoir une variable de contexte <request>
    NOTE : Aucun middleware n'est appelé pour les vues incluses
    """
    # Découper les tokens envoyés au tag
    tokens = token.split_contents()
    if len(tokens) == 1:
        raise TemplateSyntaxError(u"%(tag)s requires one or more arguments" % {'tag': token.contents.split()[0]})
    tokens.pop(0)  # Pop le nom du tag de la liste sans l'utiliser
    url_or_view = tokens.pop(0)  # Pop le nom de la vue ou de l'URL
    args, kwargs = [], {}
    # Parcourir les tokens restants. Ceux avec "=" sont des kwargs, les autres
    # deviennent des args
    for token in tokens:
        equals = token.find("=")
        if equals == -1:
            args.append(token)
        else:
            kwargs[str(token[:equals])] = token[equals + 1:]
    return ViewNode(url_or_view, args, kwargs)


def do_view_func(parser, token):
    """
    Afficher le contenu d'une vue, à l'aide de son nom de fonction uniquement
    ex. {% view "mymodule.views.inner" [arg_expr] [kwarg=expr] %}
    IMPORTANT : Le template appelant doit avoir une variable de contexte <request>
    NOTE : Aucun middleware n'est appelé pour les vues incluses
    :type token: django.template.base.Token
    """
    # Découper les tokens envoyés au tag
    tokens = token.split_contents()[1:]  # sans le token 'panel'
    if len(tokens) > 0:
        view = tokens.pop(0)  # 'nom de fonction'
        args, kwargs = [], {}
        # Parcourir les tokens restants. Ceux avec "=" sont des kwargs, les autres des args
        for token in tokens:
            subtokens = [item for item in token.split('=') if item]
            if len(subtokens) == 1:
                args.append(token)
            elif len(subtokens) == 2:
                kwargs[subtokens[0]] = subtokens[1]
            else:
                raise TemplateSyntaxError(u"Syntax error at panel argument {argument}".format(argument=token))
        return ViewFuncNode(view, args, kwargs)
    raise TemplateSyntaxError(u"{tag} requires one or more arguments".format(tag=token.contents.split()[0]))

# Enregistrer les tags
register.tag('panel', do_view_func)
register.tag('panel_url', do_view)
