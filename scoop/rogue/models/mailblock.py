# coding: utf-8
from disposable_email_checker import DisposableEmailChecker
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.fields import EmailField
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from scoop.core.abstract.core.datetime import DatetimeModel


class MailBlockManager(models.Manager):
    """ Manager des blocages d'emails """

    # Getter
    def is_valid(self, email):
        """ Renvoyer si une adresse email a un format valide """
        field = EmailField()
        try:
            field.clean(email)
            return True
        except ValidationError:
            return False

    def is_invalid(self, email):
        """ Renvoyer si une adresse email a un format invalide """
        return not self.is_valid(email)

    def is_blocked(self, email):
        """ Renvoyer si une adresse email est bloquée """
        return self.is_invalid(email) or self.is_disposable(email) or self.filter(email__icontains=email, active=True).exists()

    def is_disposable(self, email):
        """ Renvoyer si une adresse email est de type jetable """
        return self.is_invalid(email) or DisposableEmailChecker().is_disposable(email)

    # Setter
    def block(self, email, user=None, reason="", details="", domain_only=False):
        """ Bloquer une adresse email ou son nom de domaine """
        if domain_only is True and '@' in email:
            email = email.split('@')[1].strip()
        return self.update_or_create(email=email, user=user, reason=reason)

    def unblock(self, email):
        """ Débloquer une adresse email """
        self.filter(email=email).update(active=False)


class MailBlock(DatetimeModel):
    """ Blocage d'adresse email """

    # Constantes
    REASONS = [[0, _("Fake accounts")], [1, _("Raw behaviour")]]

    # Champs
    email = models.CharField(max_length=48, db_index=True, unique=True, verbose_name=_("Email address"))
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name=_("User"))
    reason = models.SmallIntegerField(choices=REASONS, default=0, verbose_name=_("Reason"))
    details = models.CharField(max_length=64, default=False, blank=True, verbose_name=_("Details"))
    active = models.BooleanField(default=True, verbose_name=pgettext_lazy('mailblocking', "Active"))
    objects = MailBlockManager()

    # Getter
    def is_valid(self):
        """ Renvoyer si la chaîne de filtre est valide """
        email_valid = self.email.count('@') < 2
        return email_valid

    # Overrides
    def __str__(self):
        """ Renvoyer une représentation unicode de l'objet """
        return _("Blocking of email {mail}").format(mail=self.email)

    # Métadonnées
    class Meta:
        verbose_name = _("mail blocking")
        verbose_name_plural = _("mail blocking")
        app_label = 'rogue'
