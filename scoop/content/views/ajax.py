# coding: utf-8
from django.http.response import HttpResponse
from scoop.content.models.attachment import Attachment
from scoop.content.models.picture import Picture
from scoop.core.util.django.forms import handle_upload
from scoop.user.models.user import User


def upload_picture_ajax(request, **kwargs):
    """ Uploader une image par morceaux """
    upload_data = handle_upload(request)
    if isinstance(upload_data, dict):
        picture = Picture.objects.create_from_file(upload_data['path'], **(kwargs.get('data', {})))
        # Ajouter l'image comme image temporaire de la session
        request.session['transient_picture'] = picture.uuid
        return picture
    return HttpResponse()


def upload_picture_profile(request, uuid):
    """ Uploader une image par morceaux et définir un propriétaire """
    user = User.objects.get_by_uuid(uuid)
    upload_picture_ajax(request, data={'author': user, 'content_object': user.profile})
    return HttpResponse()


def upload_picture_profile_main(request, uuid):
    """ Uploader une image, définir un propriétaire et définir comme image principale """
    user = User.objects.get_by_uuid(uuid)
    result = upload_picture_ajax(request, data={'author': user, 'content_object': user.profile})
    if isinstance(result, Picture):
        user.profile.set_picture(result)
    return HttpResponse()


def upload_attachment_ajax(request, **kwargs):
    """ Uploader un fichier joint par morceaux """
    upload_data = handle_upload(request)
    if isinstance(upload_data, dict):
        attachment = Attachment.objects.create_from_file(upload_data['path'], **(kwargs.get('data', {})))
        # Ajouter l'image comme image temporaire de la session
        request.session['transient_attachment'] = attachment.uuid
        return attachment
    return HttpResponse()
