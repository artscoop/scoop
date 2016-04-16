# coding: utf-8
from django.contrib.auth.decorators import user_passes_test

from scoop.rogue.models.ipblock import IPBlock
from scoop.user.access.models.ip import IP
from scoop.user.util.auth import is_superuser


@user_passes_test(is_superuser)
def block_ip(request, ip_string):
    """ Bloquer une IP """
    IPBlock.objects.block_ips(ip_string)


@user_passes_test(is_superuser)
def unblock_ip(request, ip_string):
    """ Débloquer une IP """
    IPBlock.objects.filter(ip=IP.get_ip_value(ip_string), type=0).update(active=False)
