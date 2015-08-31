# coding: utf-8
from __future__ import absolute_import

from django.db import models
from django.utils.translation import ugettext_lazy as _

from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.user.authored import AuthoredModel
from scoop.core.util.model.model import SingleDeleteManager
from scoop.forum.util.signals import poll_vote_cast


class VoteManager(SingleDeleteManager):
    """ Manager des votes """

    # Actions
    def cast(self, author, poll, choice):
        """ Voter dans un sondage """
        if choice in poll.choices.all():
            vote, created = self.get_or_create(author=author, poll=poll, choice=choice)
            if created:
                poll_vote_cast.send(vote)


class Vote(DatetimeModel, AuthoredModel):
    """ Réponse dans un sondage """
    poll = models.ForeignKey('forum.Poll', null=False, related_name='votes', verbose_name=_("Poll"))
    choice = models.SmallIntegerField(default=None, null=True, verbose_name=_("Choice"))
    objects = VoteManager()

    # Overrides
    def __unicode__(self):
        """ Représentation unicode de l'objet """
        return _(u'Vote: {vote} in poll "{poll}"').format(poll=self.poll, vote=self.choice)

    # Métadonnées
    class Meta:
        unique_together = (('author', 'poll'),)
        verbose_name = _("vote")
        verbose_name_plural = _("votes")
        app_label = 'forum'
