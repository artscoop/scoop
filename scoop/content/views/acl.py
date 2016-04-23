# coding: utf-8
from urllib import parse

from django.conf import settings
from django.http.response import HttpResponse
from scoop.core.abstract.content.acl import ACLModel
from scoop.core.util.django.apps import is_installed
from scoop.user.models.user import User

ACL_ENABLED = getattr(settings, 'CONTENT_ACL_ENABLED', True)
ACL_MEDIA = getattr(settings, 'CONTENT_ACL_MEDIA_URL', '/acl/')
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
    path_folders = filter(None, resource.split('/', 5))
    granted = not ACL_ENABLED or user.is_staff  # Autoriser par défaut si settings.CONTENT_ACL_ENABLED est False

    # Traiter l'autorisation par le nom du premier répertoire
    if not granted and len(path_folders) and path_folders[0] in ACLModel.ACL_PATHS_START:
        if path_folders[0] == ACLModel.ACL_PATHS[ACLModel.PUBLIC]:
            granted = True
        elif path_folders[0] == ACLModel.ACL_PATHS[ACLModel.PRIVATE]:
            username = path_folders[4]  # les indices 1 2 et 3 font partie du hash de spread ici
            if user.username == username:
                granted = True
        elif path_folders[0] == ACLModel.ACL_PATHS[ACLModel.FRIENDS] and is_installed('scoop.user.social'):
            username = path_folders[4]  # les indices 1 2 et 3 font partie du hash de spread ici
            path_user = User.objects.get_by_name(username)
            if user.friends.is_friend(path_user) or username == user.username:
                granted = True
        elif path_folders[0] == ACLModel.ACL_PATHS[ACLModel.REGISTERED]:
            if user.is_authenticated():
                granted = True
        else:
            granted = True
    else:
        # Toujours considérer le fichier comme public dans les cas inconnus
        granted = True

    # Demander à nginx de servir le fichier ou renvoyer un contenu HTTP403
    if granted is True:
        response = HttpResponse(content_type="")
        response['X-Accel-Redirect'] = ACL_MEDIA + parse.quote(resource)  # il faut renvoyer une URL quotée à nginx
        return response
    else:
        return DENIED_RESPONSE
