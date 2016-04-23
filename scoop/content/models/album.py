# coding: utf-8
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.content.picture import PicturedModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.generic import NullableGenericModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.social.access import PrivacyModel
from scoop.core.util.model.model import SingleDeleteManager


class AlbumManager(SingleDeleteManager):
    """ Manager des albums d'images """

    # Getter
    def for_user(self, user):
        """ Renvoyer les albums d'un utilisateur """
        return self.filter(author=user) if user else self

    def get_count_for_user(self, user):
        """ Renvoyer le nombre d'albums de l'utilisateur """
        return self.for_user(user).count()

    def get_by_uuid(self, uuid):
        """ Renvoyer l'album ayant un UUID spécifique """
        try:
            return self.get(uuid=uuid)
        except Album.DoesNotExist:
            return None

    # Setter
    def create_with(self, name, pictures, **kwargs):
        """ Créer un album et y intégrer une liste d'images """
        description = kwargs.get('description', '')
        author = kwargs.get('author', None)
        album = self.create(name=name, description=description, author=author)
        for picture in pictures:
            try:
                album.pictures.add(picture)
            except (ValueError,):
                pass


class Album(NullableGenericModel, DatetimeModel, PicturedModel, PrivacyModel, UUID64Model, WeightedModel):
    """ Album d'images """

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="albums", on_delete=models.SET_NULL, verbose_name=_("Author"))
    name = models.CharField(max_length=96, blank=False, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('album', "Updated"))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_("Parent"))
    visible = models.BooleanField(default=True, verbose_name=pgettext_lazy('album', "Visible"))
    objects = AlbumManager()

    # Getter
    def get_default_picture(self):
        """ Renvoyer l'image la plus importante de l'album """
        pictures = self.pictures.all().order_by('-weight')
        return pictures[0] if pictures.exists() else None

    def get_children_count(self, recursive=True):
        """ Renvoyer le nombre de sous-albums """
        subalbums = Album.objects.filter(parent=self)
        subcount = subalbums.count()
        if recursive is True:
            for album in subalbums:
                subcount += album.get_children_count()
        return subcount

    def get_children(self):
        """ Renvoyer les sous-albums directs """
        return Album.objects.filter(parent=self)

    # Setter
    def add(self, pictures):
        """ Insérer une image dans l'album """
        pictures = [pictures] if not isinstance(pictures, list) else pictures
        for picture in pictures:
            self.pictures.add(picture)

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.parent == self:
            self.parent = None
        super(Album, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """ Renvoyer l'URL de l'objet """
        return reverse_lazy('content:view-category', args=[self.short_name])

    def __str__(self):
        """ Renvoyer la version texte de l'objet """
        return "Picture album {name} by {author}".format(name=self.name, author=self.author)

    # Métadonnées
    class Meta:
        verbose_name = _("picture album")
        verbose_name_plural = _("picture albums")
        app_label = 'content'
