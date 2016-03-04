# coding: utf-8
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import ugettext_lazy as _
from scoop.content.models.content import Content
from scoop.core.templatetags.text_tags import humanize_join
from scoop.core.util.data.typeutil import make_iterable
from scoop.core.util.signals import record
from scoop.messaging.models.alert import Alert
from scoop.messaging.models.thread import Thread
from scoop.user.util.auth import is_staff


@user_passes_test(is_staff)
def ban_and_alert(request, users):
    """ Bannir les profils et alterter les utilisateurs qui ont été en contact """
    users, banned = make_iterable(users), []
    if users:
        for user in users:
            if user.profile.ban():
                recipients = Thread.objects.related_users(user, ack=True)
                Alert.objects.alert(recipients, 'user.profile.fake', 'security', {'profile': user.profile})
                record.send(get_user_model(), request.user, 'user.ban-alert.user', user)
                banned.append(user)
        if banned:
            messages.success(request, humanize_join(banned, 3, _("user has been banned;users hae been banned")))
            return True
    return False


@user_passes_test(is_staff)
def remove_pictures(request, users):
    """ Retirer toutes les images d'un profil """
    users, destroyed = make_iterable(users), []
    if users:
        for user in users:
            pictures = user.profile.get_pictures()
            count = pictures.count()
            if count > 0:
                Alert.objects.alert(user, 'user.profile.picture.invalid', 'notification', {'count': count, 'pictures': pictures})
                record.send(get_user_model(), request.user, 'content.delete.picture', user)
                pictures.delete()
                destroyed.append(user)
        if destroyed:
            messages.success(request, humanize_join(destroyed, 3, _("user has images removed;users have images removed")))
            return True
    messages.info(request, _("No picture has to be deleted."))
    return False


@user_passes_test(is_staff)
def lock_content(request, content):
    """ Verrouiller un contenu contre les modifications """
    if content.lock():
        Alert.objects.alert(content.get_authors(), 'content.content.lock', 'notification', {'content': content})
        messages.success(request, _("The content was locked and protected from user interaction."))
        record.send(Content, request.user, 'content.lock.content', content)
        return True
    return False
