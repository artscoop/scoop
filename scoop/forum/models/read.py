# coding: utf-8
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.util.model.model import SingleDeleteManager
from scoop.forum.util.read import default_expiry


class ReadManager(SingleDeleteManager):
    """ Manager de sujets lus """

    # Getter
    def get_unread_topics(self, user):
        """ Renvoyer les sujets non lus par un utilisateur """
        from scoop.content.models.content import Content
        # Filtrer
        return Content.objects.filter(category__short_name__iexact=Read.CONTENT_TYPE).exclude(read__isnull=True, read__user=user)

    def get_updated_topics(self, user):
        """ Renvoyer les sujets mis à jour depuis la dernière lecture """
        from scoop.content.models.content import Content
        # Renvoyer les sujets
        try:
            criteria = {'updated__gt': Read.objects.filter(category__short_name__iexact=Read.CONTENT_TYPE, user=user).latest('created').created}
            topics = Content.objects.filter(category__short_name__iexact=Read.CONTENT_TYPE, **criteria)
            return topics
        except:
            return Content.objects.none()

    def is_read(self, content, user):
        """ Renvoyer si un contenu a été lu par un utilisateur """
        return self.get(content=content, user=user, created__gt=content.updated).exists()

    # Setter
    def set_for(self, content, user):
        """ Indiquer qu'un contenu a été lu """
        if user.is_authenticated() and content.category.short_name == Read.CONTENT_TYPE:
            read, created = self.get_or_create(content=content, user=user)
            if not created:
                read.save(update_fields=['created'])
            return True
        return False

    def unset(self, content):
        """ Indiquer qu'un contenu n'a pas été lu """
        self.filter(content=content).delete()


class Read(models.Model):
    """ Statut lu pour un contenu """

    # Constante
    CONTENT_TYPE = 'forum'

    # Champs
    content = models.ForeignKey("content.Content", null=False, on_delete=models.CASCADE, related_name='reads', verbose_name=_("Thread"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name='content_reads+', verbose_name=_("User"))
    expiry = models.DateTimeField(default=default_expiry, null=True, verbose_name=_("Expiry"))
    created = models.DateTimeField(auto_now=True, verbose_name=pgettext_lazy('forum.read', "Created"))
    objects = ReadManager()

    # Métadonnées
    class Meta:
        unique_together = (('content', 'user'),)
        verbose_name = _("topic read")
        verbose_name_plural = _("topics read")
        app_label = "forum"
