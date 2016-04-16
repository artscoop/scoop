# coding: utf-8
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
        """
        Voter dans un sondage

        :param author: utilisateur auteur du vote
        :param poll: objet sondage
        :param choice: indice de la réponse à la question
        """
        if choice in poll.choices.all():
            vote, created = self.get_or_create(author=author, poll=poll, choice=choice)
            if created:
                poll_vote_cast.send(vote)


class Vote(DatetimeModel, AuthoredModel):
    """ Réponse dans un sondage """

    # Champs
    poll = models.ForeignKey('forum.Poll', null=False, related_name='votes', verbose_name=_("Poll"))
    choice = models.SmallIntegerField(default=None, blank=True, null=True, verbose_name=_("Choice"))
    objects = VoteManager()

    # Overrides
    def __str__(self):
        """ Représentation unicode de l'objet """
        return _('Vote: {vote} in poll "{poll}"').format(poll=self.poll, vote=self.choice)

    # Métadonnées
    class Meta:
        unique_together = (('author', 'poll'),)
        verbose_name = _("vote")
        verbose_name_plural = _("votes")
        app_label = 'forum'
