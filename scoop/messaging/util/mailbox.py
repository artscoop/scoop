# coding: utf-8
from __future__ import absolute_import

import logging
from mailbox import Maildir, NoSuchMailboxError
from os.path import expanduser, join
from pwd import getpwnam

logger = logging.getLogger(__name__)


def get_maildir(username):
    """ Renvoyer un répertoire de mails pour un utilisateur système """
    try:
        if isinstance(username, basestring) and getpwnam(username):
            user_home = expanduser('~{}'.format(username))  # chemin /home (ex. /root pour root)
            maildir = Maildir(join(user_home, 'Maildir'), factory=None)
            return maildir
        return None
    except KeyError as e:
        print "KE", e
        logger.error(u"The user account for {} does not exist".format(username))
    except NoSuchMailboxError as e:
        print "NSMBE", e
        logger.error(u"The user mailbox directory {} does not exist. Either postfix was not configured properly, or this user cannot have a maildir".format(e.message))
    except OSError as e:
        print "OSE", e
        logger.error(u"Most likely, this user does not exist but it was not detected")
    except Exception as e:
        print "UE", e
        logger.error(u"Uncaught exception")
    return None


def get_maildir_mails(username, set_read=False):
    """ Renvoyer les mails d'un répertoire """
    maildir = get_maildir(username)
    if maildir is not None:
        maildir.lock()
        output = {}
        for _key, message in maildir.iteritems():
            if set_read is True:
                message.set_subdir('cur')
                message.add_flag('S')
            if message.is_multipart():
                print message.get_subdir()
                submessages = message.get_payload()
                for message in submessages:
                    print "=" * 80
                    print message.as_string()
        maildir.flush()
        maildir.close()
    return output
