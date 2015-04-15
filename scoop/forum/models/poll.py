# coding: utf-8
from __future__ import absolute_import

from autoslug.fields import AutoSlugField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from scoop.core.abstract import AuthoredModel, DatetimeModel, UUID128Model
from scoop.core.abstract.content.picture import PicturableModel
from scoop.core.util.model.fields import LineListField
from scoop.core.util.model.model import SingleDeleteManager
from scoop.core.util.shortcuts import addattr


class PollManager(SingleDeleteManager):
    """ Manager des sondages """

    # Getter
    def get_by_natural_key(self, uuid):
        """ Renvoyer un sondage par sa clé naturelle """
        return self.get(uuid=uuid)

    def by_author(self, author):
        """ Renvoyer les sondages créés par un utilisateur """
        return self.filter(author=author)

    def get_by_slug(self, slug):
        """ Renvoyer un sondage par son slug """
        return self.get(slug=slug)


class Poll(DatetimeModel, AuthoredModel, UUID128Model, PicturableModel):
    """ Sondage """
    # Champs
    title = models.CharField(max_length=192, blank=False, verbose_name=_(u"Title"))
    description = models.TextField(verbose_name=_(u"Description"))
    published = models.BooleanField(default=True, db_index=True, verbose_name=pgettext_lazy('poll', u"Published"))
    expires = models.DateTimeField(null=True, blank=True, verbose_name=_(u"Expires"))
    answers = LineListField(default="Yes\nNo", blank=False, help_text=_(u"Enter one answer per line"), verbose_name=_(u"Answers"))
    slug = AutoSlugField(max_length=100, populate_from='title', unique=True, blank=True, editable=False, unique_with=('id',))
    closed = models.BooleanField(default=False, db_index=True, verbose_name=pgettext_lazy('poll', u"Closed"))
    content = models.ForeignKey('content.Content', null=True, blank=True, on_delete=models.SET_NULL, related_name='polls', verbose_name=_(u"Content"))
    objects = PollManager()

    # Getter
    def natural_key(self):
        """ Renvoyer la clé naturelle du sondage """
        return (self.uuid,)

    def get_choices(self):
        """ Renvoyer les choix du sondage triés par poids """
        return self.answers.values()

    def get_choice(self, choice):
        """ Renvoyer le texte d'un choix """
        return self.answers.get(choice, None)

    def get_form_choices(self):
        """ Renvoyer les choix de champ de formulaire """
        return tuple(enumerate(self.answers))

    @addattr(boolean=True, short_description=_(u"Has votes"))
    def has_votes(self):
        """ Renvoyer s'il y a des votes pour ce sondage """
        return self.votes.all().exists()

    def get_votes(self):
        """ Renvoyer les votes du sondage """
        return self.votes.all()

    def get_vote_count(self):
        """ Renvoyer le nombre de votes du sondage """
        return self.votes.only('pk').count()

    def get_vote_percent(self, choice):
        """ Renvoyer le pourcentage de votes sur un choix """
        total = self.get_vote_count()
        count = self.votes.filter(choice=choice)
        return count * 100.0 / total

    def get_vote_percents(self):
        """ Renvoyer un dictionnaire des pourcentages de votes """
        result = []
        for choice in self.answers.keys():
            percent = self.get_vote_percent(choice)
            result.append({'choice': choice, 'percent': percent})
        return result

    @addattr(boolean=True, short_description=_(u"Expired"))
    def has_expired(self):
        """ Renvoyer si le sondage a expiré """
        return (timezone.now() < self.expires)

    @addattr(boolean=True, short_description=_(u"Open"))
    def is_open(self):
        """ Renvoyer si le sondage est ouvert """
        return not (self.has_expired() or self.closed)

    # Setter
    def close(self):
        """ Fermer le sondage """
        if not self.closed:
            self.closed = True
            self.save()

    # Overrides
    def __unicode__(self):
        """ Renvoyer la représentation unicode de l'objet """
        return u"%s" % self.title

    # Métadonnées
    class Meta:
        app_label = 'forum'
        verbose_name = _(u"poll")
        verbose_name_plural = _(u"polls")
