# coding: utf-8
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch.dispatcher import receiver
from easy_thumbnails.signals import saved_file
from scoop.content.models.animation import Animation
from scoop.content.models.picture import Picture
from scoop.content.tasks.picture import generate_aliases
from scoop.core.util.signals import record

TARGET_MODELS_EXCLUDE_FROM_UPDATE = {}


@receiver(saved_file)
def generate_thumbnails(sender, fieldfile, **kwargs):
    """ Traiter l'enregistrement d'un nouveau fichier image """
    generate_aliases.delay(model=sender, pk=fieldfile.instance.pk, field=fieldfile.field.name)


@receiver(pre_save, sender=Picture)
def picture_presave(sender, instance, **kwargs):
    """ Traiter une image avant qu'elle soit enregistrée """
    if instance.author is None or instance.author.has_perm('content.can_download_description_picture'):
        instance.update_from_description()


@receiver(post_save, sender=Picture)
def picture_created(sender, instance, raw, created, using, update_fields, **kwargs):
    """ Traiter une image après son enregistrement """
    if created:
        Animation.objects.create_from_animation(instance)
        instance.resize()
        instance.fix_exif()
        instance.optimize()
        instance.set_correct_extension()
        instance.update_size()
        record.send(sender, actor=instance.author, action='content.create.picture', target=instance)
    # Réenregistrer l'objet lié (généralement Picturable)
    if instance.content_object and instance.content_object._meta.model_name not in TARGET_MODELS_EXCLUDE_FROM_UPDATE:
        instance.content_object.save()


@receiver(post_delete, sender=Picture)
def picture_deleted(sender, instance, **kwargs):
    """ Traiter une image après sa suppression """
    record.send(None, actor=instance.author, action='content.delete.picture', target=instance)
    if instance.content_object and instance.content_object._meta.model_name not in TARGET_MODELS_EXCLUDE_FROM_UPDATE:
        instance.content_object.save()
