# coding: utf-8
import mimetypes

from django.conf import settings
from django.http.response import HttpResponse
from os.path import join

from scoop.core.abstract.content.acl import ACLModel
from scoop.user.models.user import User


def manage_acl_file_service(request):
    """
    Traiter une requête à un chemin dans les répertoires avec ACL

    :param request: HTTPRequest
    :type request: django.http.HTTPRequest
    """
    resource = request.path
    user = request.user
    media_path = join(settings.MEDIA_ROOT, resource)
    content_type = mimetypes.guess_type(media_path)
    resource_items = [item for item in resource.split('/') if item][1:]  # retirer la partie MEDIA_URL
    response = HttpResponse(content_type=content_type)
    granted = False
    # Traiter le chemin
    if len(resource_items) and resource_items[0] in ACLModel.ACL_PATHS_START:
        if user.is_staff:
            granted = True
        elif resource_items[0] == ACLModel.ACL_PATHS[ACLModel.PUBLIC]:
            granted = True
        elif resource_items[0] == ACLModel.ACL_PATHS[ACLModel.PRIVATE]:
            username = resource_items[4]  # les indices 1 2 et 3 font partie du hash de spread
            if user.username == username:
                granted = True
        elif resource_items[0] == ACLModel.ACL_PATHS[ACLModel.FRIENDS]:
            username = resource_items[4]  # les indices 1 2 et 3 font partie du hash de spread
            path_user = User.objects.get_by_name(username)
            if user.friends.is_friend(path_user):
                granted = True
        elif resource_items[0] == ACLModel.ACL_PATHS[ACLModel.REGISTERED]:
            if user.is_authenticated():
                granted = True
        else:
            granted = True
    else:
        # Toujours considérer le fichier comme public dans les cas inconnus
        granted = True
    if granted is True:
        resource = resource.replace(settings.MEDIA_URL, '/acl_media/', 1)
        response['X-Accel-Redirect'] = resource
        print("ACL granted to {path}".format(path=resource))
    else:
        response.status_code = 403
        response.content = 'Access denied'
        print("Access denied to {path}".format(path=resource))
    return response

