# coding: utf-8
from annoying.functions import get_object_or_None
from autoslug.fields import AutoSlugField
from django.conf import settings
from django.db import models
from django.db.models import permalink
from django.db.models.aggregates import Sum
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.icon import IconModel
from scoop.core.abstract.core.weight import WeightedModel
from scoop.core.abstract.social.access import AccessLevelModel
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.shortcuts import addattr
from scoop.forum.tasks.forum import recalculate_topic_count


class ForumManager(models.Manager):
    """ Manager des forums """

    # Getter
    def _get_dummy_forum(self):
        """ Renvoyer un faux forum d'index """
        return Forum(name=_("Forum index"))

    def get_root_forums(self):
        """ Renvoyer les forums de la racine """
        return self.filter(root=True).order_by('id')

    def get_by_id(self, fid):
        """ Renvoyer un forum par son id """
        forum = get_object_or_None(Forum, id=fid)
        if forum is None:
            forum = self._get_dummy_forum()
        return forum

    def get_by_slug(self, slug):
        """ Renvoyer un forum par son slug """
        forum = get_object_or_None(Forum, slug=slug)
        if forum is None:
            forum = self._get_dummy_forum()
        return forum

    def get_children(self, forum):
        """ Renvoyer les enfants d'un forum """
        if forum is None or forum.pk is None:
            return self.get_root_forums()
        return forum.forums.all()

    def is_circular(self, root=None):
        """ Renvoyer si la liste des forums possède un lien circulaire """

        # Fonction récursive qui renvoie la profondeur de l'arborescence
        def get_max_depth(self, level=0, root=None, limit=24):
            level = level + 1
            if level < limit:
                root = self.get_root_forums() if root is None else root
                for forum in root:
                    level = get_max_depth(self, level=level, root=forum.get_forums())
                return level
            else:
                return limit

        return get_max_depth(self, root=root) >= 15


class Forum(IconModel, WeightedModel, DatetimeModel, AccessLevelModel):
    """ Forum """

    # Champs
    name = models.CharField(max_length=80, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    locked = models.BooleanField(default=False, help_text=_("Protected from the creation of new topics"), verbose_name=pgettext_lazy('forum', "Locked"))
    visible = models.BooleanField(default=True, verbose_name=pgettext_lazy('forum', "Visible"))
    slug = AutoSlugField(max_length=100, populate_from='name', unique=True, blank=True, editable=True, unique_with=('id',))
    # Cache du nombre de sujets
    topic_count = models.IntegerField(default=0, verbose_name=_("Topics count"))
    post_count = models.IntegerField(default=0, verbose_name=_("Posts count"))
    # Forum parent
    root = models.BooleanField(default=False, blank=True, help_text=_("Appears on the forum index"), verbose_name=_("Root"))
    forums = models.ManyToManyField('forum.Forum', blank=True, related_name='parents', verbose_name=_("Subforums"))
    # Sujets contenus dans le forum
    topics = models.ManyToManyField('content.Content', blank=True, limit_choices_to={'category__short_name__in': ['topic', 'forum']}, related_name="forums", verbose_name=_("Topics"))
    # Modérateurs du forum
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='moderated_forums', help_text=_("Members who can moderate topics in this forum"),
                                        verbose_name=_("Moderators"))
    objects = ForumManager()

    # Overrides
    @python_2_unicode_compatible
    def __str__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return str(self.name)

    def __repr__(self):
        """ Renvoyer la représentation ASCII de l'objet """
        return "Forum: {}".format(self.__str__())

    @permalink
    def get_absolute_url(self):
        """ Renvoyer l'URL du forum """
        return ('forum:forum-view', [self.id])

    # Getter
    def get_parents(self):
        """ Renvoyer les parents du forum """
        return self.parents.all()

    def get_latest_topic(self):
        """ Renvoyer le dernier sujet du forum """
        return self.topics.latest('updated')

    def get_latest_comment(self):
        """ Renvoyer le dernier commentaire du forum """
        topic = self.get_latest_topic()
        if topic is not None:
            comment = topic.get_last_comment()
        return comment or topic

    def get_topics(self, admin=False):
        """ Renvoyer les sujets du forum """
        topics = self.topics
        if not admin:
            topics = topics.filter(published=True)
        return topics

    def get_forums(self):
        """ Renvoyer les sous-forums """
        return self.forums.all()

    @addattr(admin_order_field='topic_count', short_description=_("Topics"))
    def get_topic_count(self):
        """ Renvoyer le nombre de sujets du forum """
        count = self.topics.count()
        for forum in self.forums.all():
            count += forum.get_topic_count()
        # Définir le compte de topics et sauvegarder si différent
        if self.topic_count != count:
            self.topic_count = count
            self.save(update_fields=['topic_count'])
        return count

    @addattr(allow_tags=True, short_description=_("Topics"))
    def get_topic_count_admin(self):
        """ Renvoyer la représentation admin du nombre de sujets dans le forum """
        return "<center><span class='badge'>{count}</span></center>".format(count=self.get_topic_count())

    @addattr(admin_order_field='post_count', short_description=_("Posts"))
    def get_post_count(self):
        """ Renvoyer le nombre de posts du forum et de ses descendants """
        count = self.topics.all().aggregate(comments=Sum('comment_count'))
        for forum in self.forums:
            count += forum.get_post_count()
        return count

    def has_topic(self, content):
        """ Renvoyer si un sujet fait partie du forum """
        return self.topics.filter(id=content.pk).exists()

    def is_moderator(self, user):
        """ Renvoyer si un utilisateur est modérateur du forum """
        return user in self.moderators.all() or user.is_superuser

    @addattr(boolean=True, short_description=_("Has forums"))
    def has_forums(self):
        """ Renvoyer s'il y a des sous-forums """
        return self.forums.exists()

    @addattr(boolean=True, short_description=_("Locked"))
    def is_locked(self):
        """ Renvoyer si le forum est verrouillé """
        return self.locked

    @addattr(boolean=True, short_description=_("Group"))
    def is_group(self):
        """ Le forum est-il juste un regroupement de forums """
        return self.has_forums() and self.is_locked()

    def is_visible(self, user):
        """ Renvoyer si le forum est visible par un utilisateur """
        return self.is_accessible(user) and self.visible

    @addattr(boolean=True, short_description=_("Circular"))
    def is_circular(self):
        """ Renvoyer si le forum est parent d'une structure circulaire ? (infinie) """
        return Forum.objects.is_circular(root=self)

    def can_add(self, user=None):
        """ Renvoyer si le forum peut recevoir un nouveau sujet """
        return not self.locked or (user and user.is_staff)

    # Setter
    def add(self, topics, user=None):
        """ Ajouter un sujet au forum """
        if self.can_add(user):
            for topic in make_iterable(topics):
                if topic.type.short_name in ['topic', 'forum']:
                    self.topics.add(topic)
                    return True
        return False

    def remove(self, topics, wipe=False):
        """ Retirer un sujet du forum """
        for topic in make_iterable(topics):
            self.topics.remove(topic)
            if wipe is True:
                topic.delete()

    def move(self, topics, forum):
        """ Déplacer des sujets vers un autre forum """
        for topic in make_iterable(topics):
            if self.has_topic(topic):
                forum.topics.add(topic)
                self.topics.remove(topic)

    def copy(self, topics, forum):
        """ Copier des sujets dans un autre forum """
        for topic in make_iterable(topics):
            if self.has_topic(topic):
                forum.topics.add(topic)

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        if self.id is not None:
            getattr(recalculate_topic_count, 'delay')(self)
        super(Forum, self).save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("forum")
        verbose_name_plural = _("forums")
        app_label = 'forum'
