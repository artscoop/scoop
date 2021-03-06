# coding: utf-8
from ajax_select import make_ajax_form
from django.contrib import admin
from django.contrib.admin.options import ModelAdmin
from django.utils.formats import localize
from django.utils.translation import ugettext_lazy as _
from scoop.content.forms.animation import AnimationForm
from scoop.content.models.animation import Animation
from scoop.core.util.shortcuts import addattr


@admin.register(Animation)
class AnimationAdmin(ModelAdmin):
    """ Modération des animations vidéo (via GIF) """

    list_select_related = True
    list_display = ['id', 'get_picture_id', 'picture', 'get_video_tag', 'extension', 'title', 'get_file_size', 'get_duration_unit', 'autoplay', 'loop',
                    'deleted']
    list_display_links = ['id']
    list_filter = ['picture__content_type']
    form = make_ajax_form(Animation, {'author': 'user', 'picture': 'picture'}, AnimationForm)
    actions = ['delete_full']

    @addattr(short_description=_("Fully delete selected animations"))
    def delete_full(self, request, queryset):
        """ Action : Supprimer les animations du queryset """
        for animation in queryset:
            animation.delete(clear=True)
        self.message_user(request, _("Selected animation has been fully deleted."))

    @addattr(allow_tags=True, short_description=_("Video"))
    def get_video_tag(self, obj):
        """ Renvoyer le tag HTML d'un objet vidéo """
        return obj.get_html(width=160)

    @addattr(short_description=_("Img.#"))
    def get_picture_id(self, obj):
        """ Renvoyer l'id de l'image source de l'animation """
        if obj.picture:
            return "{}".format(obj.picture.id)

    @addattr(short_description=_("Duration"))
    def get_duration_unit(self, obj):
        """ Renvoyer un texte de la durée de l'animation """
        duration = obj.get_duration()
        minutes, seconds = divmod(duration, 60.0)
        return ("{minutes:.0f}m{seconds}s" if minutes else "{seconds}s").format(minutes=minutes, seconds=localize(seconds))
