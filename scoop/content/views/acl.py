# coding: utf-8
import logging

from django.conf import settings
from django.http.response import HttpResponse

from scoop.core.abstract.content.acl import ACLModel
from scoop.core.util.django.apps import is_installed
from scoop.user.models.user import User


logger = logging.getLogger('acl')
ACL_ENABLED = getattr(settings, 'CONTENT_ACL_ENABLED', True)
DENIED_RESPONSE = HttpResponse(status=403)


def acl_file_serve(request, resource):
    """
    Traiter une requête à un chemin dans les répertoires avec ACL

    Renvoie un objet HTTPResponse avec éventuellement un header X-Accel-Redirect pointant
    vers une *location* nginx portant la directive internal.
    :param request: HTTPRequest
    :param resource: chemin du fichier relatif au répertoire media
    :type request: django.http.HTTPRequest
    :type resource: str
    :returns: un objet HTTPResponse
    """
    user = request.user
    path_folders = [item for item in resource.split('/', 5) if item]
    granted = not ACL_ENABLED or user.is_staff  # Autoriser par défaut si settings.CONTENT_ACL_ENABLED est False

    # Traiter l'autorisation par le nom du premier répertoire
    if not granted and len(path_folders) and path_folders[0] in ACLModel.ACL_PATHS_START:
        if path_folders[0] == ACLModel.ACL_PATHS[ACLModel.PUBLIC]:
            logger.debug("ACL: Public file {0}".format(resource))
            granted = True
        elif path_folders[0] == ACLModel.ACL_PATHS[ACLModel.PRIVATE]:
            logger.debug("ACL: Private file {0}".format(resource))
            username = path_folders[4]  # les indices 1 2 et 3 font partie du hash de spread ici
            if user.username == username:
                granted = True
        elif path_folders[0] == ACLModel.ACL_PATHS[ACLModel.FRIENDS] and is_installed('scoop.user.social'):
            username = path_folders[4]  # les indices 1 2 et 3 font partie du hash de spread ici
            path_user = User.objects.get_by_name(username)
            logger.debug("ACL: File accessible only to friends of {1}, {0}".format(resource, username))
            if user.friends.is_friend(path_user) or username == user.username:
                granted = True
        elif path_folders[0] == ACLModel.ACL_PATHS[ACLModel.REGISTERED]:
            logger.debug("ACL: File accessible only to registered users, {0}".format(resource))
            if user.is_authenticated():
                granted = True
        else:
            logger.debug("ACL: File processing not ready yet, {0}".format(resource))
            granted = True
    else:
        # Toujours considérer le fichier comme public dans les cas inconnus
        logger.debug("ACL: Unrecognized public file, {0}".format(resource))
        granted = True

    # Demander à nginx de servir le fichier ou renvoyer un contenu HTTP403
    if granted is True:
        response = HttpResponse(content_type="")
        response['X-Accel-Redirect'] = '/acl_media/%s' % resource
        logger.debug("ACL: Access granted to file {path}".format(path=resource))
        return response
    else:
        logger.debug("ACL: Access denied to file {path}".format(path=resource))
        return DENIED_RESPONSE
