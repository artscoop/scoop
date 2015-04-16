# coding: utf-8
""" Contenus texte """
from __future__ import absolute_import

import logging
import operator
from datetime import date, timedelta
from operator import itemgetter

import markdown
import textile
from autoslug.fields import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.template.defaultfilters import striptags, truncatewords
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from fuzzywuzzy import fuzz
from ngram import NGram
from translatable.exceptions import MissingTranslation
from translatable.models import TranslatableModel, get_translation_model

from scoop.content.util.signals import content_pre_lock
from scoop.core.abstract.content.comment import CommentableModel
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.abstract.core.data import DataModel
from scoop.core.abstract.core.generic import NullableGenericModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.moderation import ModeratedModel, ModeratedQuerySetMixin
from scoop.core.abstract.core.translation import TranslationModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.seo.index import SEIndexModel, SEIndexQuerySetMixin
from scoop.core.abstract.social.access import PrivacyModel
from scoop.core.abstract.user.ippoint import IPPointableModel
from scoop.core.util.data.dateutil import is_new
from scoop.core.util.data.textutil import clean_html, text_to_dict
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.django.templateutil import render_block_to_string
from scoop.core.util.model.model import SingleDeleteManager, SingleDeleteQuerySetMixin
from scoop.core.util.shortcuts import addattr

logger = logging.getLogger(__name__)


class ContentQuerySetMixin(object):
    """ Mixin de Manager et Queryset """

    def by_request(self, request):
        """ Renvoyer les éléments accessibles à l'utilisateur """
        return self.visible() if not request.user.is_staff else self

    def visible(self, **kwargs):
        """ Renvoyer les éléments visibles """
        return self.filter(published=True, deleted=False, **(kwargs or dict())).order_by('-sticky')

    def invisible(self, **kwargs):
        """ Renvoyer les éléments invisibles """
        return self.filter(published=False, deleted=False, **(kwargs or dict())).order_by('-sticky')

    def deleted(self, **kwargs):
        """ Renvoyer les contenus marqués comme supprimés """
        return self.filter(deleted=True)

    def featured(self, **kwargs):
        """ Renvoyer les contenus magazine (mis en avant) """
        return self.visible(featured=True)

    def by_author(self, user):
        """ Renvoyer les contenus créés par un utilisateur """
        return self.filter(authors=user)

    def get_by_slug(self, slug, exact=True, category=None, exc=None):
        """
        Renvoyer le contenu correspondant à un slug
        :param slug: slug du contenu à retrouver
        :param exact: échouer si le slug exact n'existe pas
        :param category: nom du type de contenu
        :param exc: classe de l'exception à lever si le slug exact n'existe pas
        """
        slug = unicode(slug)
        try:
            return self.get(slug=slug)
        except Content.DoesNotExist:
            if exact:
                if exc is None:
                    raise
                else:
                    raise exc(u"No content found with this slug")
        word = max(slug.split('-'), key=len)  # utiliser le mot le plus long pour filtrer
        contents = self.filter(slug__icontains=word, **({'category': category} if category is not None else {}))  # filtrer les contenus contenant le mot le plus long
        try:
            closest = max([{'ratio': similarity, 'content': content} for content, similarity in zip(contents, map(lambda x: fuzz.ratio(slug, x.slug) * fuzz.partial_ratio(slug, x.slug), contents)) if similarity > 7500], key=operator.itemgetter('ratio'))
            return closest['content']
        except:
            return None

    def get_by_id(self, cid, exc=None):
        """
        Renvoyer le contenu ayant un ID précis
        :param cid: id du contenu à retrouver
        :param exc: exception à lever si l'ID n'existe pas
        """
        try:
            return self.get(pk=cid)
        except:
            if exc is None:
                raise
            raise exc()

    def by_category(self, categories, attribute='short_name', **kwargs):
        """
        Renvoyer les contenus correspondant à des catégories précises
        :param categories: liste de catégories ou liste de noms de catégories
        :param attribute: sur quel attribut de la classe catégorie effectuer la recherche
        """
        categories = make_iterable(categories, list)
        ctype = type(categories[0])
        kwargs.update({('category__{}__in' if issubclass(ctype, basestring) else 'category__in').format(attribute): categories})
        return self.filter(**kwargs)

    def by_tags(self, tags, **kwargs):
        """
        Renvoyer les contenus ayant des étiquettes précises
        :param tags: liste de noms de tags ou liste de tags
        :param kwargs: options de filtrage supplémentaires
        """
        tags = make_iterable(tags, list)
        ttype = type(tags[0])
        return self.filter(tags__short_name__in=tags, **kwargs) if issubclass(ttype, basestring) else self.filter(terms__in=tags, **kwargs)

    def get_months(self, *args, **kwargs):
        """ Renvoyer la liste des mois de publication des articles """
        return self.visible(**kwargs).datetimes('created', 'month', order='DESC')

    def get_days(self, *args, **kwargs):
        """ Renvoyer la liste des jours de publication des articles """
        return self.visible(**kwargs).datetimes('created', 'day', order='DESC')

    def by_month(self, month, *args, **kwargs):
        """
        Renvoyer les contenus créés pendant un mois
        :param month: date ou datetime situé dans le mois désiré
        """
        kwargs.update({'created__month': month.month, 'created__year': month.year})
        return self.visible(**kwargs).order_by('-created')

    def on_day(self, day, *args, **kwargs):
        """
        Renvoyer les contenus créés un jour précis
        :param day: date ou datetime situé dans le jour désiré
        """
        return self.visible().filter(created__year=day.year, created__month=day.month, created__day=day.day).order_by('-id')

    def get_last_edit_time(self, **kwargs):
        """ Renvoyer la date la plus récente de modification des contenus """
        try:
            return self.filter(**kwargs).latest('edited').edited
        except:
            return timezone.now()

    # Setter
    def delete_from_author(self, author=None):
        """ Effacer les contenus d'un auteur """
        if author is not None:
            return self.filter(authors=author).update(deleted=True)

    def unpublish_from_author(self, author=None):
        """ Dépublier les contenus d'un auteur """
        if author is not None:
            return self.filter(authors=author).update(published=False)

    def publish_every(self, start=None, step=None):
        """
        Publier les contenus (max. 128 contenus) progressivement
        :param start: date correspondant au premier jour de publication
        :param step: à quel intervalle publier les contenus
        """
        # Par défaut, demain à 7h toutes les 24h
        start = start or date.today() + timedelta(days=1, hours=7)
        step = step or timedelta(days=1)
        # Retarder la publication des articles
        if self.count() <= 128 and self.exists():
            for content in self.all().order_by('id'):
                if not content.published:
                    content.update(save=True, publish=start)
                    start += step
            return True
        logger.warn(u"You can schedule publication for 1 to 128 contents max.")
        return False


class ContentQuerySet(models.QuerySet, ContentQuerySetMixin, ModeratedQuerySetMixin, SEIndexQuerySetMixin, SingleDeleteQuerySetMixin):
    """ Queryset des contenus """
    pass


class ContentManager(models.Manager.from_queryset(ContentQuerySet), models.Manager, ContentQuerySetMixin, ModeratedQuerySetMixin, SEIndexQuerySetMixin):
    """ Manager des contenus """

    def create(self, authors, category, title, body, visible=True, **kwargs):
        """
        Créer un nouveau contenu
        :param authors: auteur ou liste des utilisateurs auteurs
        :param category: nom de catégorie du nouveau contenu
        :param title: titre du contenu
        :param body: texte du contenu
        :param visible: définir si le contenu est visible du public
        """
        try:
            [kwargs.pop(name, None) for name in ['category', 'title', 'body', 'visible']]
            category_instance = Category.objects.get_by_name(category)
            content = Content(category=category_instance, title=title, body=body, published=visible, **kwargs)
            content.save()
            authors = make_iterable(authors, list)
            content.authors.add(*authors)
            return content
        except AttributeError:
            return None


class CategoryManager(SingleDeleteManager):
    """ Manager des types de contenus """

    def get_by_name(self, name):
        """ Renvoyer un type de contenu selon nom de code """
        candidates = self.filter(short_name__iexact=name)
        return candidates.first() if candidates.exists() else None

    def get_by_url(self, url):
        """ Renvoyer un type de contenu selon son url"""
        candidates = self.filter(url=url.lower())
        return candidates.first() if candidates.exists() else None


class Content(ModeratedModel, NullableGenericModel, PicturableModel, PrivacyModel, CommentableModel, UUID64Model, IPPointableModel, DataModel, WeightedModel, SEIndexModel):
    """ Contenu basé sur du texte """
    # Constantes
    DEFAULT_TEASER_SIZE = 20  # Taille du teaser en mots
    FORMATS = {0: _(u"Plain HTML"), 1: _(u"Markdown"), 2: _(u"Textile")}
    FORMAT_CHOICES = FORMATS.items()
    TRANSFORMS = {1: markdown.Markdown().convert, 2: textile.textile}  # fonctions à appliquer à chaque format
    DATA_KEYS = ['similar']

    # Champs
    category = models.ForeignKey('content.Category', null=False, related_name='contents', verbose_name=_(u"Category"))
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='contents', verbose_name=_(u"Authors"))
    title = models.CharField(max_length=192, blank=False, verbose_name=_(u"Title"))
    body = models.TextField(blank=True, verbose_name=_(u"Text"))
    html = models.TextField(blank=True, help_text=_(u"HTML output from body"), verbose_name=_(u"HTML"))
    teaser = models.TextField(blank=True, verbose_name=_(u"Introduction"))
    format = models.SmallIntegerField(choices=FORMAT_CHOICES, default=0, verbose_name=_(u"Format"))
    slug = AutoSlugField(max_length=100, populate_from='title', unique=True, blank=True, editable=True, unique_with=('id',))
    picture = models.ForeignKey('content.Picture', null=True, blank=True, on_delete=models.SET_NULL, related_name='contents', help_text=_(u"Main picture"), verbose_name=_(u"Picture"))
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', verbose_name=_(u"Follow up of"))
    tags = models.ManyToManyField('content.Tag', blank=True, related_name='contents', verbose_name=_(u"Classification tags"))
    # Toutes les dates du contenu
    deleted = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('content', u"Deleted"))
    created = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=pgettext_lazy('content', u"Created"))
    edited = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=pgettext_lazy('content', u"Edited"))
    updated = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=pgettext_lazy('content', u"Updated"))
    publish = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Publish when"))
    expire = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Unpublish when"))
    # État du contenu
    published = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('content', u"Published"))
    sticky = models.BooleanField(default=False, db_index=True, help_text=_(u"Will stay on top of lists"), verbose_name=pgettext_lazy('content', u"Sticky"))
    featured = models.BooleanField(default=False, db_index=True, help_text=_(u"Will appear in magazine editorial content"), verbose_name=pgettext_lazy('content', u"Featured"))
    locked = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('content', u"Locked"))
    objects = ContentManager()

    # Getter
    @addattr(boolean=True, short_description=_(u"Published"))
    def is_published(self):
        """ Renvoyer si le contenu est publié """
        now = timezone.now()
        published = self.published or (self.publish and self.publish < now and (self.expire is None or self.expire > now))
        if published and self.published is False:
            self.update(published=True, save=True)
        return published

    @addattr(short_description=_(u"Commentable"))
    def is_commentable(self):
        """ Renvoyer si le contenu peut être commenté """
        return self.commentable and not self.locked

    def is_editable(self, user):
        """ Renvoyer si le contenu peut être modifié par un utilisateur """
        return self.authors.filter(id=user.id).exists() or user.is_staff or user.is_superuser

    @addattr(short_description=_(u"Authors"))
    def get_authors(self):
        """ Renvoyer les utilisateurs auteurs du document """
        return self.authors.all()

    def is_author(self, user):
        """ Renvoyer si un utilisateur fait partie des auteurs du document """
        return self.authors.filter(pk=user.pk).exists()

    @addattr(short_description=_(u"Authors count"))
    def get_author_count(self):
        """ Renvoyer le nombre d'auteurs du document """
        return self.authors.count()

    def get_html(self):
        """ Renvoyer le HTML non échappé du document """
        return mark_safe(self.html)

    @addattr(boolean=True, short_description=_(u"New"))
    def is_new(self, days=3):
        """ Renvoyer si le contenu a été publié dans les n derniers jours """
        show_date = self.publish if (self.publish is not None and self.publish > self.created) else self.created
        return is_new(show_date, days)

    def get_similarity(self, content):
        """
        Renvoyer l'indice de similarité avec un autre contenu
        :returns: similarité entre 0.0 et 1.0, 1.0 étant l'identité
        """
        labels = {'title', 'body', 'tags'}
        this, that = ({label: render_block_to_string("content/similarity/content.djhtml", item, {'content': self}) for label in labels} for item in [self, content])
        weights = text_to_dict(render_to_string("content/similarity/weights.txt", {}), evaluate=True)  # texte de la forme key:value\n
        return sum([NGram.compare(this[label], that[label]) * weights[label] for label in labels]) / sum(weights.values())

    @addattr(short_description=_(u"Teaser"))
    def get_teaser(self, words=DEFAULT_TEASER_SIZE):
        """ Renvoyer le résumé du document (automatique) """
        if len(self.teaser) <= 8 and len(self.body) > 8:
            self.teaser = truncatewords(self.body, words)
            self.save()
        return self.teaser

    def get_teaser_text(self):
        """ Renvoyer le résumé du document, sans balise HTML """
        return striptags(self.get_teaser())

    @addattr(short_description=_(u"Similar content"))
    def similar_to(self):
        """ Renvoyer les contenus publiés les plus similaires à ce contenu """
        similar = self.get_data('similar')
        return Content.objects.visible().filter(id__in=similar or [])

    @addattr(boolean=True, short_description=_(u"Has similar content"))
    def has_similar(self):
        """ Renvoyer si le contenu recense des contenus similaire """
        similar = self.get_data('similar')
        return similar is not None and len(similar) > 0

    @addattr(short_description=_(u"Tags"))
    def get_tags(self):
        """ Renvoyer les tags du document """
        return self.tags.all()

    @addattr(short_description=_(u"Children"))
    def get_children(self):
        """ Renvoyer les contenus enfants, triés par poids/page """
        return self.children.all().order_by('weight')

    def get_siblings(self):
        """ Renvoyer les contenus ayant le même parent que ce document """
        return Content.objects.filter(parent=self.parent).exclude(id=self.id) if self.parent else Content.objects.none()

    def fetch_picture(self, force=False, count=1):
        """ Récupérer automatiquement des images correspondant aux tags du document """
        default = "{tags}".format(tags=u" ".join(unicode(tag) for tag in self.get_tags()))
        fallback = "{title}".format(title=self.title)
        return self._fetch_pictures(default, fallback, count, self.author, force)

    def get_category_url(self):
        """ Renvoyer le tronçon spécifique d'URL du type du contenu """
        return self.category.url.lower()

    def has_category_url(self, url):
        """ Renvoyer si le tronçon d'URL de la catégorie du type est celui demandé """
        return self.get_category_url() == url.lower()

    @permalink
    def get_absolute_url(self):
        """ Renvoyer l'URL du contenu """
        return ('content:content-view', [], {'category': self.category.url, 'slug': self.slug})

    # Privé
    def _populate_html(self):
        """ Définir le code HTML selon le corps original du document """
        self.html = Content.TRANSFORMS.get(self.format, lambda s: s)(self.body)

    def _populate_similar(self, repopulate=False, result_count=10, categories=None):
        """
        Définir la liste des documents similaires à ce document
        :param repopulate: recréer la liste même si elle existe déjà
        :param result_count: nombre maximum de contenus similaires à enregistrer
        :param categories: liste de types de contenu à choisir ou None
        """
        if self.is_published() and (not self.get_data('similar') or repopulate is True):
            items = Content.objects.visible(category__in=[self.category] if categories is None else categories).exclude(id=self.id).distinct().iterator()
            matches = {item.id: self.get_similarity(item) for item in items}
            matches = sorted(matches.items(), key=itemgetter(1))[0:result_count]
            self.set_data('similar', [item[0] for item in matches])
            return True
        return False

    # Setter
    def undelete(self):
        """ Marquer le contenu comme non supprimé """
        self.update({'deleted': False}, save=True)

    def clean_body(self):
        """ Nettoyer et assainir la sortie HTML du document """
        self.html = clean_html(self.html)

    def clean_tags(self):
        """ Supprimer les tags correspondant à un autre type de contenu """
        for tag in self.get_tags():
            if tag.category != self.category:
                self.tags.remove(tag)

    def set_publish_dates(self, start, end):
        """ Définir les dates de publication et d'expiration """
        self.publish = start
        self.expire = end
        self.save(update_fields=['start', 'end'])

    def publish_plain(self, value):
        """ Publier ou dépublier un contenu """
        self.published = value
        self.publish = None
        self.expire = None
        self.save()

    def lock(self, value=True, author=None):
        """ Verrouiller administrativement un contenu """
        if self.locked != value:
            result = content_pre_lock.send(None, instance=self, author=author, value=value)
            if not [False for item in result if item[1] is False]:
                self.locked = value
                self.save(update_fields=['locked'])

    def add_author(self, author):
        """ Ajouter un utilisateur aux auteurs du document """
        if author is not None:
            self.authors.add(author)
            return True

    def remove_author(self, author):
        """ Retirer un utilisateur des auteurs du document """
        try:
            self.authors.remove(author)
            return True
        except:
            return False

    # Overrides
    def __init__(self, *args, **kwargs):
        """ Constructeur """
        super(Content, self).__init__(*args, **kwargs)
        self.__original_body = self.body

    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.updated = timezone.now()
        super(Content, self).save(*args, **kwargs)

    def __unicode__(self):
        """ Renvoyer la représentation unicode """
        return self.title

    # Métadonnées
    class Meta:
        verbose_name = _(u"content")
        verbose_name_plural = _(u"contents")
        # Pas de traduction paresseuse des permissions (https://code.djangoproject.com/ticket/13965)
        permissions = (("can_access_all_content", u"Can bypass content access"),)
        get_latest_by = 'updated'
        ordering = ['-edited']
        app_label = 'content'


class Category(TranslatableModel, IconModel, DataModel):
    """ Type de contenu """
    # Champs
    short_name = models.CharField(max_length=10, verbose_name=_(u"Identifier"))
    url = models.CharField(max_length=16, help_text=_(u"e.g. blog, story or article"), verbose_name=_(u"URL"))
    has_index = models.BooleanField(default=True, verbose_name=_(u"Has index"))
    visible = models.BooleanField(default=True, verbose_name=_(u"Visible"))
    objects = CategoryManager()

    # Getter
    @addattr(short_description=_(u"Name"))
    def get_name(self):
        """ Renvoyer le nom au singulier du type de contenu """
        try:
            return self.get_translation().name
        except MissingTranslation:
            return _(u"(No name)")

    @addattr(short_description=_(u"Plural"))
    def get_plural(self):
        """ Renvoyer le nom au pluriel du type de contenu """
        try:
            return self.get_translation().plural
        except MissingTranslation:
            return _(u"(No name)")

    @addattr(short_description=_(u"Description"))
    def get_description(self):
        """ Renvoyer la description du type de contenu """
        try:
            return self.get_translation().description
        except MissingTranslation:
            return _(u"(No description)")

    def get_contents(self, **kwargs):
        """ Renvoyer tous les contenus correspondant à ce type """
        return self.contents.filter(**kwargs)

    # Propriétés
    name = property(get_name)
    plural = property(get_plural)
    description = property(get_description)

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        self.url = self.url.lower().strip()
        super(Category, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """ Supprimer l'objet de la base de données """
        if not self.content_set.all().exists():
            super(Category, self).delete(*args, **kwargs)

    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return unicode(self.get_name())

    # Métadonnées
    class Meta:
        verbose_name = _(u"content type")
        verbose_name_plural = _(u"content types")
        app_label = 'content'


class CategoryTranslation(get_translation_model(Category, "category"), TranslationModel):
    """ Traduction de type de contenu """
    # Champs
    name = models.CharField(max_length=48, blank=False, verbose_name=_(u"Name"))
    plural = models.CharField(max_length=48, blank=False, default="__", verbose_name=_(u"Plural"))
    description = models.TextField(blank=True, verbose_name=_(u"Description"))

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.plural == self._meta.get_field('plural').default:
            self.plural = "{}s".format(self.name)
        super(CategoryTranslation, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        app_label = 'content'
        verbose_name = _(u"translation")
        verbose_name_plural = _(u"translations")
