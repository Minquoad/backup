# BACKUP

## Contexte

Ce projet est à la fois une base de code mais aussi un lieu de réflexion sur comment sauvegare mes données.

J'ai un serveur linux avec pleins de containers remplissants différents services comme :

- wordpress (un container mariadb:11 + un container wordpress)
- nextcloud (un container mariadb:11 + un container nextcloud)
- home-assistant (un container ghcr.io/home-assistant/home-assistant:stable)

La liste n'est pas exhaustive mais on va commencer par là.

Toutes les données persistantes des containers sont dans des volumes docker-compose, c.-à-d. des bind-mount donc dans des dossiers directement accessibles sans docker.
Le tout doit être sauvegardé à chaud.

Je veux donc sauvegarder pour l'instant deux types de choses :

- des base de données mariadb:11
- des dossiers de fichiers

## Bases de données

Pour les bases de données ça peut se faire par `mariadb-dump ...`. La taille de ces fichiers est assez raisonnable pour en garder un bon nombre avec une rotation gérée par `backup_cleaner.py`.

Cette solution pour les bdd me convient, il faudra cependant la centraliser ici.
La solution doit être entièrement containerisée afin de ne rien installer sur la machine (mariadb-client par exemple).

## Fichiers

Historiquement, je sauvegardais les dossiers :

- /opt/nextcloud/app-data
- /opt/blog-justine/wordpress-data
- /opt/home-assistant/data

en générant des `*.tar.gz` de ces derniers avec une rotation gérée par `backup_cleaner.py`.

Problème : la données est dipliquée (3 backup = trois fois la place occupée).

Le but de ce projet est de centraliser la gestion de ces backup et de trouver une solution au problème de l'espace occupé par les `*.tar.gz`.

Une solution avec un comportement git-like serait bien pour pouvoir revenir dans le temps à n'importe quel moment mais sans dupliquer le stockage.
