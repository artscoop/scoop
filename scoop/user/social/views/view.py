# coding: utf-8
from annoying.decorators import render_to
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound


@render_to("user/panels/view-user-list-simple.html", string=True)
def view_user_friends(request, user=None):
    """ Afficher la liste des amis d'un utilisateur """
    if user is None:
        return HttpResponseNotFound()
    users = user.friends.get_users()
    return {'users': users, 'user': user}


@render_to("user/panels/view-user-list-simple.html", string=True)
@user_passes_test(lambda u: u.is_authenticated())
def view_common_friends(request, user=None):
    """ Afficher la liste des amis communs avec un utilisateur """
    if user is None:
        return HttpResponseNotFound()
    users = user.friendlist.get_mutual_users(request.user, count=False)
    return {'users': users, 'title': u"Amis communs (%d)" % len(users), 'size': 4, 'nested': True}
