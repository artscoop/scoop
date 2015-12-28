# coding: utf-8
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.contenttypes.fields import ContentType
from django.db import models
from django.db.utils import IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.content.models.content import Content
from scoop.core.abstract.core.datetime import DatetimeModel
from scoop.core.abstract.core.generic import GenericModel
from scoop.core.abstract.core.uuid import UUID64Model
from scoop.core.util.data.dateutil import from_now
from scoop.core.util.shortcuts import addattr
from scoop.messaging.util.signals import mailable_event


class SubscriptionManager(models.Manager):
    """ Manager des abonnements """

    # Getter
    def for_email(self, email, confirmed=None):
        """
        Renvoyer les abonnements pour une adresse email
        :param confirmed: Renvoyer les abonnements confirmés (True), en attente (False) ou tous (None)
        """
        return self.filter(email__iexact=email, **({'confirmed': confirmed} if confirmed is not None else {})) if email else self

    def for_content(self, content):
        """ Renvoyer tous les abonnements confirmés pour le contenu """
        content_type = ContentType.objects.get_for_model(content)
        return self.filter(content_type=content_type, object_id=content.pk, confirmed=True)

    # Actions
    def subscribe(self, content, email):
        """ Ajouter un abonnement """
        if isinstance(content, Content):
            try:
                subscription = Subscription(email=email.lower())
                subscription.content_object = content
                subscription.save()
                mailable_event.send(sender=content, category='staff', mailtype='content.subscription.confirm', recipient=subscription.email, data={})
                return True
            except IntegrityError:
                return False

    def confirm(self, uuid):
        """
        Confirmer un abonnement portant l'UUID demandé
        :returns: True si un abonnement en attente est confirmé, False sinon
        """
        subscriptions = self.filter(uuid=uuid, confirmed=False)
        if subscriptions.exists():
            subscriptions.update(confirmed=True)
            return True
        return False

    def unsubscribe_all(self, email):
        """
        Retirer tous les abonnements pour cette adresse mail
        :returns: True s'il y avait des abonnements en cours, False sinon
        """
        subscriptions = self.for_email(email)
        if subscriptions.exists():
            subscriptions.delete()
            return True
        return False

    def unsubscribe(self, email, *items):
        """ Se désabonner de 1 ou plusieurs contenus """
        updated_rows = 0
        for item in items:
            updated_rows += self.for_content(item).filter(email__iexact=email, confirmed=True).update(confirmed=False)
        return updated_rows > 0

    def purge(self):
        """ Supprimer les abonnement non-validés dans les 6 dernières heures """
        self.filter(time__gt=from_now(hours=-6, timestamp=True)).delete()


class Subscription(GenericModel, DatetimeModel, UUID64Model):
    """ Abonnement """

    # Champs
    email = models.EmailField(max_length=96, verbose_name=_("Email"))
    confirmed = models.BooleanField(default=False, verbose_name=pgettext_lazy('content.subscription', "Confirmed"))
    objects = SubscriptionManager()

    # Getter
    @addattr(short_description=pgettext_lazy('content.subscription', "Confirmed"))
    def is_confirmed(self):
        """ Renvoyer si l'abonnement est confirmé """
        return self.confirmed

    # Overrides
    def save(self, *args, **kwargs):
        """ Enregistrer l'objet dans la base de données """
        super().save(*args, **kwargs)

    # Métadonnées
    class Meta:
        verbose_name = _("content subscription")
        verbose_name_plural = _("content subscriptions")
        unique_together = [['content_type', 'object_id', 'email']]
        app_label = 'content'
