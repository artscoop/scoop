# Projet Scoop
Par S. Kossouho
Mai 2011 - Mars 2016
Séparé du projet One le 15 avril 2015

## Contenu du projet
- `content` : objets de contenu, images et commentaires. lié à `user` et `core`.
- `editorial` : partie CMS du système, possibilité d'enregistrer des extraits de texte et d'agencer les contenus dans des templates.
- `forum` : hiérarchie de conteneurs de sujets de discussion.
- `location` : représentation en base de données de pays, villes et lieux réels.
- `messaging` : communication privée entre utilisateurs, et file de mails/alertes, etc.
- `user` : tout ce qui concerne un utilisateur.
- `user.access` : tout ce qui concerne les accès au site des utilisateurs.
- `rogue` : ce qui concerne les contenus, utilisateurs et comportements indésirables.
- `location` : ce qui concerne pays, villes et lieux.
- `core` : le cœur du projet, contient tous les utilitaires et modèles utiles au moteur.
- `user.social` : options sociales comme like, amitié et événements.
- `user.social.people` : mise en logique de personnes réelles.

## Settings

### Content
- `CONTENT_WEBLOG_PING` : *bool*, ping des services de blog lorsque les contenus sont mis à jour
- `GENERICRELATION_PICTURE_FILTER` : *dict*, par défaut, comment filtrer les images attachées au objets PicturableModel
- `DEFAULT_THUMBNAIL_DIMENSIONS` : *dict*, dimensions par défaut d'une miniature, avec les clés `width` et `height`
- `CLASSIFY_LANGUAGE` : *str*, langue par défaut des stopwords, parmi ['english', 'french']

### Core
- `CORE_ACTION_RECORD` : *bool*, faut-il enregistrer les actions core.Record dans la base de données
- `FORM_ALIASES` : *dict*, alias utilisés pour identifier les formulaires à valider en AJAX (voir scoop.core.views.ajax.validate_form)
- `MAKEMESSAGES_DIRS` : *list*, liste de répertoires racines à parcourir à la recherche de locales à traduire

### Messaging
- `MESSAGING_MAX_BATCH` : *int*, nombre de mails à envoyer au maximum par batch d'envoi. 30 par défaut
- `MESSAGING_MAIL_SENDER` : *str*, expéditeur par défaut pour l'application. DEFAULT_FROM_EMAIL par défaut
- `MESSAGING_DEFAULT_THREAD_QUOTA` : *int*, nombre de threads que peut ouvrir un utilisateur par défaut par jour. 10 par défaut
- `MESSAGING_BLACKLIST_ENABLE` : *bool*, autoriser la mise en liste noire pour la messagerie. False par défaut
- `MESSAGING_THREAD_UNIQUE` : *bool*, la création de thread doit-elle réutiliser les threads existants. True par défaut
- `MESSAGING_THREAD_TOGGLE_DELAY` : *int*, délai minimum en secondes avant de pouvoir modifier l'état ouvert/fermé d'un thread. 3600 par défaut
