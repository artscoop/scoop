# coding: utf-8
from django_inlines import inlines
from django_inlines.inlines import TemplateInline


class ExcerptInline(TemplateInline):
    """ Inline d'extrait """
    inline_args = []

    def get_context(self):
        """ Renvoyer le contexte d'affichage du template """
        from scoop.editorial.models import Excerpt
        identifier = self.value
        # Vérifier que l'image existe
        try:
            excerpt = Excerpt.objects.get(name=identifier)
        except Excerpt.DoesNotExist:
            excerpt = None
        return {'excerpt': excerpt}

    def get_template_name(self):
        """ Renvoyer le chemin du template d'affichage """
        base = super(ExcerptInline, self).get_template_name()[0]
        path = "editorial/%s" % base
        return path


# Enregistrer les classes d'inlines
inlines.registry.register('snip', ExcerptInline)
