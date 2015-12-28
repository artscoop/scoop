# coding: utf-8
"""
Inlines de templates
Voir https://github.com/blturner/django_inlines
"""
from django_inlines import inlines
from django_inlines.inlines import TemplateInline


class ContentInline(TemplateInline):
    """
    Inline d'insertion de contenus
    Format : {{content uuid [style=stylename]}}
    Exemple : {{content identifier style="link"}}
    """
    inline_args = [{'name': 'style'}]

    def get_context(self):
        """ Renvoyer un contexte pour le rendu de l'inline """
        from scoop.content.models.content import Content

        uuid = self.value
        style = self.kwargs.get('style', 'link')  # style par défaut : lien
        # Vérifier que le contenu demandé existe
        contents = Content.objects.visible().filter(uuid=uuid)
        content = contents[0] if contents.exists() else None
        return {'content': content, 'style': style}

    def get_template_name(self):
        """ Renvoyer le chemin du template """
        base = super(ContentInline, self).get_template_name()[0]
        path = "content/{0}".format(base)
        return path


class ContentPictureInline(TemplateInline):
    """
    Inline d'insertion d'images liées aux contenus
    Format : {{content_image index [css_class=name]}}
    Exemple : {{content_image 1 css_class="class1"}}
    """
    inline_args = [{'name': 'size'}, {'name': 'class'}]

    def get_context(self):
        """ Renvoyer le contexte de rendu de l'inline """
        ind = int(self.value) - 1  # index 1-based
        content = self.context['content']  # la variable content doit exister dans le contexte du template
        size = self.kwargs.get('size', False)
        css_class = "{0}{1}".format(" " if "class" in self.kwargs else "", self.kwargs.get('class', ""))
        # Vérifier que l'image demandée existe
        images = content.get_pictures()
        image = images[ind] if 0 <= ind <= images.count() else None
        return {'image': image, 'size': size, 'class': css_class}

    def get_template_name(self):
        """ Renvoyer le chemin du template """
        base = super(ContentPictureInline, self).get_template_name()[0]
        path = "content/%s" % base
        return path


# ===============================================================================
# Inline d'intégration de liens
# Format : {{link uuid}}
# ===============================================================================
class LinkInline(TemplateInline):
    """
    Inline d'insertion de liens
    Format : {{link uuid}}
    """
    inline_args = []

    def get_context(self):
        """ Renvoyer le contexte de rendu de l'inline """
        from scoop.content.models.link import Link

        identifier = self.value
        # Vérifier que le lien demandé existe
        contents = Link.objects.filter(uuid=identifier)
        content = contents[0] if contents.exists() else None
        return {'link': content}

    def get_template_name(self):
        """ Renvoyer le chemin du template """
        base = super(LinkInline, self).get_template_name()[0]
        path = "content/{}".format(base)
        return path


class PictureInline(TemplateInline):
    """
    Inline d'insertion d'images
    Format : {{image uuid [size=widthxheight] [class=css] [radius=int]}}
    Exemple : {{image dF4y8P size="160x160" class="bordered" radius=1}}
    """
    inline_args = [{'name': 'size'}, {'name': 'class'}, {'name': 'radius'}]

    def get_context(self):
        """ Renvoyer le contexte de rendu de l'inline """
        from scoop.content.models.picture import Picture

        identifier = self.value.split()[0]
        size = self.kwargs.get('size', False)
        radius = self.kwargs.get('radius', 0)
        css_class = "{0}{1}".format(" " if "class" in self.kwargs else "", self.kwargs.get('class', ""))
        # Vérifier que l'image demandée existe
        image = Picture.objects.visible().get_by_uuid(identifier)
        return {'image': image, 'size': size, 'class': css_class, 'radius': radius}

    def get_template_name(self):
        """ Renvoyer le chemin du template """
        base = super(PictureInline, self).get_template_name()[0]
        path = "content/{}".format(base)
        return path

    @staticmethod
    def get_app_label():
        """ Renvoyer l'étiquette de l'application """
        return 'content/picture'


class AnimationInline(TemplateInline):
    """
    Inline d'insertion d'animations
    Format : {{animation imageuuid [class=css]}}
    Exemple : {{animation dF4y8P class="bordered"}}
    """
    inline_args = [{'name': 'class'}]

    def get_context(self):
        """ Renvoyer le contexte de rendu de l'inline """
        from scoop.content.models.picture import Picture

        uuid = self.value
        css_class = "{0}{1}".format(" " if "class" in self.kwargs else "", self.kwargs.get('class', ""))
        image = Picture.objects.get_by_uuid(uuid)
        return {'image': image, 'class': css_class}

    def get_template_name(self):
        """ Renvoyer le chemin du template """
        base = super(AnimationInline, self).get_template_name()[0]
        path = "content/{}".format(base)
        return path


class AlbumInline(TemplateInline):
    """
    Inline d'insertion d'album
    Format : {{album uuid [class=css]}}
    Exemple : {{album dF4y5P class="bordered"}}
    """
    inline_args = [{'name': 'class'}]

    def get_context(self):
        """ Renvoyer le contexte de rendu de l'inline """
        from scoop.content.models.album import Album

        uuid = self.value
        css_class = "{0}{1}".format(" " if "class" in self.kwargs else "", self.kwargs.get('class', ""))
        # Vérifier que l'album désiré existe
        album = Album.objects.get_by_uuid(uuid=uuid)
        return {'album': album, 'class': css_class}

    def get_template_name(self):
        """ Renvoyer les chemin du template """
        base = super(AlbumInline, self).get_template_name()[0]
        path = "content/{}".format(base)
        return path


class AttachmentInline(TemplateInline):
    """
    Inline d'insertion de pièces jointes
    Format : {{attachment uuid}}
    """
    inline_args = []

    def get_context(self):
        """ Renvoyer le contexte de rendu de l'inline """
        from scoop.content.models import Attachment

        uuid = self.value
        link = Attachment.objects.get_link_by_uuid(uuid)
        return {'link': link}

    def get_template_name(self):
        """ Renvoyer le chemin du template """
        base = super(AttachmentInline, self).get_template_name()[0]
        path = "content/{}".format(base)
        return path

# Enregistrer les classes d'inlines
inlines.registry.register('album', AlbumInline)
inlines.registry.register('attachment', AttachmentInline)
inlines.registry.register('content', ContentInline)
inlines.registry.register('content_image', ContentPictureInline)
inlines.registry.register('link', LinkInline)
inlines.registry.register('image', PictureInline)
inlines.registry.register('animation', AnimationInline)
