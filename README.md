# Projet Scoop
S. Kossouho
Mai 2011 - 2016
Séparé du projet One le 15 avril 2015

Nécessite python 3.5, nginx et Django 1.9

## Contenu du projet
- `content` : objets de contenu, images et commentaires + ACL fichiers. lié à `user` et `core`.
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
- `help` : pages d'aide, FAQ et aide contextuelle
- `analyze` : classes abstraites et helpers pour la classification de documents

## Settings

### Content
- `CONTENT_WEBLOG_PING` : *bool*, ping des services de blog lorsque les contenus sont mis à jour
- `GENERICRELATION_PICTURE_FILTER` : *dict*, par défaut, comment filtrer les images attachées au objets PicturableModel
- `DEFAULT_THUMBNAIL_DIMENSIONS` : *dict*, dimensions par défaut d'une miniature, avec les clés `width` et `height`
- `CLASSIFY_LANGUAGE` : *str*, langue par défaut des stopwords, parmi ['english', 'french']
- `CONTENT_ACL_ENABLED` : *bool* (True), si False, toujours autoriser l'accès aux fichiers media protégés par ACL 
- `CONTENT_ACL_FOLDER` : *str* ('{Y}/{M}'), chemin des fichiers contrôlés par l'ACL, sans slash au début et à la fin 
- `CONTENT_ACL_AUTO_UPDATE_PATHS` : *bool* (False), si True, chaque fichier ACL utilisera le modèle de nommage courant lors de sa sauvegarde.
- `CONTENT_ACL_MEDIA_URL` : *str*, chemin de redirection vers le répertoire _location_ internal de nginx

### Core
- `CORE_ACTION_RECORD` : *bool*, faut-il enregistrer les actions core.Record dans la base de données
- `CORE_BRAND_NAME_MARKER` : *str*, lorsque le tag text_tags.brand est utilisé, quel texte doit être remplacé par le nom du site ? ex. '%brand%'
- `MENU_ALIASES` : *dict*, alias de menus (nom: objet Menu)
- `FORM_ALIASES` : *dict*, alias utilisés pour identifier les formulaires à valider en AJAX (voir scoop.core.views.ajax.validate_form)
- `MAKEMESSAGES_DIRS` : *list*, liste de répertoires racines à parcourir à la recherche de locales à traduire
- `OPENING_HOURS` : *list*, liste de plages d'heures d'ouverture du site, si le middleware opening est actif.
- `OPENING_HOURS_GROUPS_EXCLUDE` : *list*, permet aux groupes d'outrepasser les heures de fermeture

### Messaging
- `MESSAGING_MAX_BATCH` : *int*, nombre de mails à envoyer au maximum par batch d'envoi. 30 par défaut
- `MESSAGING_MAIL_SENDER` : *str*, expéditeur par défaut pour l'application. DEFAULT_FROM_EMAIL par défaut
- `MESSAGING_DEFAULT_THREAD_QUOTA` : *int*, nombre de threads que peut ouvrir un utilisateur par défaut par jour. 10 par défaut
- `MESSAGING_BLACKLIST_ENABLE` : *bool*, autoriser la mise en liste noire pour la messagerie. False par défaut
- `MESSAGING_THREAD_UNIQUE` : *bool*, la création de thread doit-elle réutiliser les threads existants. True par défaut
- `MESSAGING_THREAD_TOGGLE_DELAY` : *int*, délai minimum en secondes avant de pouvoir modifier l'état ouvert/fermé d'un thread. 3600 par défaut

### Scoop
- `SCOOP_DISABLE_SIGNALS` : *bool*, désactiver les listeners de toutes les applications de scoop

### Migrations
- Créer les migrations avec ```dj makemigrations content core editorial forum location messaging rogue user access social```
