# coding: utf-8
from annoying.decorators import render_to

from scoop.content.models import Comment
from scoop.core.util.django.formutil import form
from scoop.user.social.forms import PostCommentForm


@render_to("social/panels/edit-comment-form.html", string=True)
def edit_feed_comment(request, feed_id=None, validate=False):
    """ Formulaire de commentaire d'un feed (?) """
    # TODO: Supprimer ce module si nécessaire
    if request.has_post('submit-feed-comment') and validate:
        form1 = form(PostCommentForm, request)
        user = request.user
        if form1.is_valid():
            body = form1.cleaned_data['comment']
            Comment.objects.comment(None, body=body, author=user, type=4)
    form1 = PostCommentForm()
    return {'validate': validate, 'form': form1}
