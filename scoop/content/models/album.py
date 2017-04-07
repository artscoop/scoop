# coding: utf-8
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.content.picture import PicturedBaseModel, PicturedModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.generic import NullableGenericModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.social.access import PrivacyModel
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.model.model import SingleDeleteManager


class AlbumManager(SingleDeleteManager):
    """ Manager des albums d'images """

    # Getter
    def for_user(self, user):
        """
        Renvoyer les albums d'un utilisateur
        
        :type user: int
        """
        return self.filter(author=user) if user else self

    def get_count_for_user(self, user):
        """ Renvoyer le nombre d'albums de l'utilisateur """
        return self.for_user(user).count()

    def get_by_uuid(self, uuid, exc=None):
        """ Renvoyer l'album ayant un UUID spécifique """
        try:
            return self.get(uuid=uuid)
        except Album.DoesNotExist:
            if exc is None:
                return None
            else:
                raise exc

    # Setter
    def create_with(self, name, pictures, **kwargs):
        """ Créer un album et y intégrer une liste d'images """
        pictures = make_iterable(pictures)
        description = kwargs.get('description', '')
        author = kwargs.get('author', None)
        album = Album(name=name, description=description, author=author)
        album.save()
        album.add(pictures)
        return album


class Album(NullableGenericModel, DatetimeModel, PicturedBaseModel, PrivacyModel, DataModel, UUID64Model, WeightedModel):
    """ Album d'images """

    # Constantes
    DATA_KEYS = ['privacy']

    # Champs
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="albums", on_delete=models.SET_NULL, verbose_name=_("Author"))
    name = models.CharField(max_length=96, blank=False, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    updated = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('album', "Updated"))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_("Parent"))
    visible = models.BooleanField(default=True, verbose_name=pgettext_lazy('album', "Visible"))
    pictured = models.BooleanField(default=False, db_index=True, verbose_name=_("\U0001f58c"))
    pictures = models.ManyToManyField('content.Picture', through='content.albumpicture', blank=True, verbose_name=_("Pictures"))
    objects = AlbumManager()

    # Getter
    def get_default_picture(self):
        """ Renvoyer l'image la plus importante de l'album """
        pictures = self.pictures.all().order_by('-album_data__weight')
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
        pictures = make_iterable(pictures)
        for picture in pictures:
            AlbumPicture.objects.get_or_create(album=self, picture=picture)
        self.save()  # Mettre à jour l'état pictured

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


class AlbumPicture(WeightedModel):
    """
    Table intermédiaire pour organiser les images dans un album

    Ajoute des informations de notes sur les images ainsi qu'un poids,
    afin de pouvoir réorganiser les images dans l'album.
    (Les images possèdent aussi un poids, qui lui est utilisé globalement)
    """

    # Champs
    notes = models.CharField(max_length=512, blank=True, verbose_name=_("Notes"))
    album = models.ForeignKey('content.album', related_name='picture_data', on_delete=models.CASCADE, verbose_name=_("Album"))
    picture = models.ForeignKey('content.picture', related_name='album_data', on_delete=models.CASCADE, help_text=_("Select a picture to link to"),
                                verbose_name=_("Picture"))

    # Métadonnées
    class Meta:
        verbose_name = _("album picture")
        db_table = 'content_album_pictures_weighted'
        unique_together = [['picture', 'album']]
        ordering = ['weight', 'pk']
        app_label = 'content'
