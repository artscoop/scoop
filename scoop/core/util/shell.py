# coding: utf-8
from __future__ import absolute_import

import sys

import pexpect


def call_and_type(command, prompt_regex, entry):
    """ Lancer une commande interactive dans le shell et y taper du contenu si un regex est affiché """
    p = pexpect.spawn(command, logfile=sys.stdout, maxread=16384)
    index = p.expect_exact([prompt_regex, pexpect.EOF])
    if index == 0:
        p.setecho(False)
        p.sendline(entry)
        while p.read():
            pass
