# coding: utf-8
from django.core.urlresolvers import reverse_lazy


class FlaggableModelUtil:
    """
    Mixin d'objet pouvant être signalé à la modération

    Monkey-patching done in scoop.core.__init__
    """

    def get_flag_url(self):
        """ Renvoyer l'URL pour signaler l'objet """
        from django.contrib.contenttypes.fields import ContentType
        content_type_id = ContentType.objects.get_for_model(self).id
        identifier = self.id
        return reverse_lazy('rogue:flag-new', args=[content_type_id, identifier])
