# coding: utf-8
from django_inlines import inlines
from django_inlines.inlines import TemplateInline
from scoop.user.models import User


class UserInline(TemplateInline):
    """
    Inline d'insertion d'utilisateur

    Format : {{user id [style=link|etc.]}}
    Exemple : {{user 2490 style="link"}}
    """
    inline_args = [{'name': 'style'}]

    def get_context(self):
        """ Renvoyer le contexte d'affichage du template """
        identifier = self.value
        style = self.kwargs.get('style', 'link')
        # Vérifier que l'utilisateur demandé existe
        user = User.objects.get_or_none(id=identifier)
        return {'user': user, 'style': style}

    def get_template_name(self):
        """ Renvoyer le chemin du template """
        base = super(UserInline, self).get_template_name()[0]
        path = "user/%s" % base
        return path

# Enregistrer les classes d'inlines
inlines.registry.register('user', UserInline)
