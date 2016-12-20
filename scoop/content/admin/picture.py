# coding: utf-8
import os

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from django.conf import settings
from django.conf.urls import patterns
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import date as datefilter
from django.utils.timezone import localtime
from django.utils.translation import ugettext_lazy as _
from genericadmin.admin import GenericAdminModelAdmin
from scoop.content.admin.filters import DimensionsFilter
from scoop.content.forms.picture import PictureAdminForm, ZipUploadForm
from scoop.content.models.picture import Picture
from scoop.core.abstract.user.authored import AutoAuthoredModelAdmin
from scoop.core.admin.filters import TimestampFilter
from scoop.core.util.django.admin import GenericModelUtil
from scoop.core.util.shortcuts import addattr
from scoop.core.util.stream.fileutil import clean_empty_folders, clean_orphans

__all__ = ['PictureAdmin']


@admin.register(Picture)
class PictureAdmin(GenericAdminModelAdmin, AjaxSelectAdmin, AutoAuthoredModelAdmin, GenericModelUtil):
    """ Administration des images """

    list_display = ['id', 'get_thumbnail', 'title', 'description', 'width', 'height', 'get_file_size', 'get_content_type_info', 'get_content_object_info',
                    'get_uuid_html', 'get_updated_date', 'get_deleted', 'acl_mode', 'moderated']
    list_filter = ['content_type', 'deleted', DimensionsFilter, 'moderated', 'acl_mode', TimestampFilter]
    list_display_links = ['id']
    list_editable = ['title', 'moderated']
    readonly_fields = ['uuid']
    list_select_related = True
    list_per_page = 20
    search_fields = ['description', 'title', 'image', 'id']
    ordering = ['-id']
    raw_id_fields = []
    actions = ['resave', 'clone', 'delete_pictures', 'delete_thumbnails', 'recalculate_size', 'fix_extension', 'optimize', 'update_picture_path',
               'clean_everything', 'rien', 'quantize', 'rien', 'contrast', 'liquid', 'remove_icc', 'autocrop', 'autocrop_extra', 'rotate90', 'rotate180',
               'rotate270', 'mirror_x', 'mirror_y', 'enhance', 'clone']
    form = make_ajax_form(Picture, {'author': 'user'}, PictureAdminForm)
    fieldsets = ((_("Picture"), {'fields': ('author', 'license', 'content_type', 'object_id', 'image', 'title', 'description', 'weight')}),
                 (_("Plus"), {'fields': ('audience', 'acl_mode')}))
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    admin_integration_enabled = True

    @addattr(short_description=_("Resave selected pictures"))
    def resave(self, request, queryset):
        """ Sauvegarder à nouveau des images (update) """
        for picture in queryset:
            picture.save()

    @addattr(short_description=_("Delete picture thumbnails"))
    def delete_thumbnails(self, request, queryset):
        """ Supprimer les miniatures des images """
        for picture in queryset:
            picture.clean_thumbnail()
        self.message_user(request, _("The selected pictures' thumbnails have been cleaned."))

    @addattr(short_description=_("Delete picture(s) permanently"))
    def delete_pictures(self, request, queryset):
        """ Effacer définitivement les images """
        for picture in queryset:
            picture.delete(clear=True)
        self.message_user(request, _("The selected pictures have been deleted."))

    @addattr(short_description=_("Recalculate selected pictures dimensions"))
    def recalculate_size(self, request, queryset):
        """ Mettre à jour les dimensions des images """
        for picture in queryset:
            picture.update_size()
        self.message_user(request, _("Dimensions were recalculated successfully."))

    @addattr(short_description=_("Fix filename extension"))
    def fix_extension(self, request, queryset):
        """ Modifier l'extension du fichier si erronée """
        for picture in queryset:
            picture.set_correct_extension()
        self.message_user(request, _("Extensions were recalculated successfully."))

    @addattr(short_description=_("Become the selected picture(s) author"))
    def take_control(self, request, queryset):
        """ Définir l'utilisateur courant comme propriétaire des images """
        for picture in queryset:
            picture.author = request.user
            picture.save()
        self.message_user(request, _("The selected pictures are now owned by you."))

    @addattr(short_description=_("Remove ICC Color Profile"))
    def remove_icc(self, request, queryset):
        """ Retirer le profil de couleur ICC des images """
        for picture in queryset:
            picture.remove_icc()
        self.message_user(request, _("The selected pictures have been converted to basic sRGB."))

    @addattr(short_description=_("Optimize file size"))
    def optimize(self, request, queryset):
        """ Optimiser la taille des fichiers des images """
        for picture in queryset:
            picture.optimize()
        self.message_user(request, _("The selected pictures have been optimized."))

    @addattr(short_description=_("Enhance"))
    def enhance(self, request, queryset):
        """ Traiter l'image afin d'améliorer son apparence """
        for picture in queryset:
            picture.enhance(False)
        self.message_user(request, _("The selected pictures have been enhanced."))

    @addattr(short_description=_("Quantize"))
    def quantize(self, request, queryset):
        """ Réduire l'image à une palette + tramage """
        for picture in queryset:
            picture.quantize(False)
        self.message_user(request, _("The selected pictures have been quantized."))

    @addattr(short_description=_("Smart resize {number} percent").format(number=60))
    def liquid(self, request, queryset):
        """ Redimensionner à 60% en retirant les détails mineurs """
        for picture in queryset:
            picture.liquid(60, 60)
        self.message_user(request, _("The selected pictures have been smart resized."))

    @addattr(short_description=_("Increase contrast"))
    def contrast(self, request, queryset):
        """ Augmenter le contraste des images """
        for picture in queryset:
            picture.contrast(False)
        self.message_user(request, _("The selected pictures contrasts have been increased."))

    @addattr(short_description=_("Clone"))
    def clone(self, request, queryset):
        """ Dupliquer les images """
        for picture in queryset:
            picture.clone()
        self.message_user(request, _("The selected pictures have been cloned."))

    @addattr(short_description=_("Autocrop"))
    def autocrop(self, request, queryset):
        """ Découper automatiquement l'image (simple) """
        for picture in queryset:
            picture.autocrop()
        self.message_user(request, _("The selected pictures have been automatically cropped."))

    @addattr(short_description=_("Autocrop by feature detection"))
    def autocrop_extra(self, request, queryset):
        """ Découper automatiquement l'image (avancé) """
        for picture in queryset:
            picture.autocrop_advanced()
        self.message_user(request, _("The selected pictures have been automatically cropped."))

    @addattr(short_description=_("Rotate 90 degrees clockwise"))
    def rotate90(self, request, queryset):
        """ Pivoter l'image à 90° dans le sens des aiguilles """
        for picture in queryset:
            picture.rotate(90)
        self.message_user(request, _("The selected pictures have been rotated."))

    @addattr(short_description=_("Rotate 180 degrees"))
    def rotate180(self, request, queryset):
        """ Pivoter l'image à 180° """
        for picture in queryset:
            picture.rotate(180)
        self.message_user(request, _("The selected pictures have been rotated."))

    @addattr(short_description=_("Rotate 90 degrees counter-clockwise"))
    def rotate270(self, request, queryset):
        """ Pivoter l'image à 90° dans le sens contraire des aiguilles """
        for picture in queryset:
            picture.rotate(-90)
        self.message_user(request, _("The selected pictures have been rotated."))

    @addattr(short_description=_("Mirror along the y axis (horizontally)"))
    def mirror_x(self, request, queryset):
        """ Effectuer une symétrie horizontale (autour de l'axe Y) """
        for picture in queryset:
            picture.mirror('x')
        self.message_user(request, _("The selected pictures have been mirrored."))

    @addattr(short_description=_("Mirror along the x axis (vertically)"))
    def mirror_y(self, request, queryset):
        """ Effectuer une symétrie verticale (autour de l'axe X) """
        for picture in queryset:
            picture.mirror('y')
        self.message_user(request, _("The selected pictures have been mirrored."))

    @addattr(short_description=_("Update the path of these pictures with current rules"))
    def update_picture_path(self, request, queryset):
        """ Mettre à jour le chemin des images en utilisant les paramètres par défaut des nouveaux fichiers """
        for picture in queryset:
            picture.update_file_path()
        self.message_user(request, _("The selected pictures paths have been updated."))

    @addattr(short_description=_("Delete empty media folders"))
    def clean_folders(self, request, queryset):
        """ Supprimer les répertoires vides """
        clean_empty_folders(settings.MEDIA_ROOT)
        self.message_user(request, _("Empty media folders have been deleted."))

    @addattr(short_description=_("Clear orphaned files and thumbnails"))
    def clean_everything(self, request, queryset):
        """ Supprimer les miniatures des fichiers et les fichiers orphelins """
        clean_orphans(delete=True)
        Picture.objects.clean_thumbnails()
        self.message_user(request, _("Orphaned files and thumbnails have been cleared."))

    @addattr(short_description="*" * 40)
    def rien(self, request, queryset):
        """ Action séparateur """
        pass

    def get_actions(self, request):
        actions = super(PictureAdmin, self).get_actions(request)
        actions.pop('delete_selected', None)
        return actions

    def get_queryset(self, request):
        """ Renvoyer le queryset par défaut """
        return Picture.objects.all()

    @addattr(allow_tags=True, admin_order_field='image', short_description=_("Path"))
    def get_image_path(self, obj):
        """ Renvoyer le chemin de l'image """
        return "{}<br><small>{}</small>".format(os.path.dirname(obj.image.name), os.path.basename(obj.image.name))

    @addattr(allow_tags=True, short_description=_("Picture"))
    def get_thumbnail(self, obj):
        """ Renvoyer une miniature HTML de l'image """
        return obj.get_thumbnail_html(size=(48, 20))

    @addattr(allow_tags=True, admin_order_field='updated', short_description=_("Upd."))
    def get_updated_date(self, obj):
        """ Renvoyer la date de dernière mise à jour """
        return '<span title="{title}">{anchor}</span>'.format(anchor=datefilter(localtime(obj.updated), "H:i"),
                                                              title=datefilter(localtime(obj.updated), "d F Y H:i"))

    @addattr(boolean=True, admin_order_field='deleted', short_description=_("Del."))
    def get_deleted(self, obj):
        """ Renvoyer si l'image est marquée comme supprimée """
        return obj.deleted

    def zip_upload(self, request):
        """ Page d'upload d'un fichier zip d'images """
        app_label = self.model._meta.app_label
        opts = self.model._meta
        form = ZipUploadForm(request.POST, request.FILES, request=request) if request.has_post() else ZipUploadForm(request=request)
        if form.is_valid():
            form.save_file(form.cleaned_data['zipfile'])
            self.message_user(request, _("File has been processed."))
        return render_to_response("admin/content/picture/upload_zip.html", {'adminform': form, 'app_label': app_label, 'opts': opts},
                                  context_instance=RequestContext(request))

    def formfield_for_dbfield(self, db_field, **kwargs):
        """ Renvoyer un champ de formulaire pour un champ db """
        return super(PictureAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_urls(self):
        """ Renvoyer les URLs disponibles pour cette page d'administration """
        urls = super(PictureAdmin, self).get_urls()
        extra = patterns('', (r'^upload_zip/$', self.admin_site.admin_view(self.zip_upload)))
        return extra + urls
