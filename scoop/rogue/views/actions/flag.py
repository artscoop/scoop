# coding: utf-8
from __future__ import absolute_import

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import ugettext_lazy as _

from scoop.core.util.signals import record
from scoop.messaging.models.alert import Alert
from scoop.messaging.models.thread import Thread
from scoop.user.util.auth import is_staff


@user_passes_test(is_staff)
def ban_and_alert(request, user, template):
    """ Bannir le profil et alterter les utilisateurs """
    action_done = user.profile.ban()
    # Créer la notice à l'utilisateur
    if action_done is True:
        recipients = Thread.objects.related_users(user)
        Alert.objects.alert(recipients, 'user.profile.fake', 'security', {'profile': user.profile})
        count = len(recipients)
        notice = _("%(user)s has been banned and reported to %(count)d users.") % {'user': user, 'count': count}
        messages.success(request, notice)
        record.send(None, request.user, 'user.ban-alert.user', user)


@user_passes_test(is_staff)
def remove_pictures(request, user):
    """ Retirer toutes les images d'un profil """
    pictures = user.profile.get_pictures()
    count = pictures.count()
    if count > 0:
        Alert.objects.alert(user, 'user.profile.picture.invalid', 'notification', {'count': count, 'pictures': pictures})
        notice = _("%(count)s pictures by %(user)s have been deleted.") % {'count': count, 'user': user}
        messages.success(request, notice)
    else:
        messages.warning(request, _("No picture was deleted."))
    pictures.delete()
    record.send(None, request.user, 'content.delete.picture', user)


@user_passes_test(is_staff)
def lock_content(request, content):
    """ Verrouiller un contenu contre les modifications """
    content.lock()
    Alert.objects.alert(list(content.authors.all()), 'content.content.lock', 'notification', {'content': content})
    messages.success(request, _("The content was protected from user interaction."))
    record.send(None, request.user, 'content.lock.content', content)
