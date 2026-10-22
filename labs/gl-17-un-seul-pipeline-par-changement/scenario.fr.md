# Scénario

Depuis que l'équipe travaille par demandes de fusion, la file du runner a
doublé. Et personne n'a ajouté de job.

Chaque push sur une branche qui porte une demande de fusion ouverte produit
**deux pipelines** pour le **même commit** : celui de la branche, et celui de la
demande de fusion. Les mêmes tests, deux fois, sur le même code. La demande de
fusion affiche deux résultats, et quand l'un est vert et l'autre rouge,
personne ne sait lequel compte.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Faites en sorte qu'un changement produise **un** pipeline, et le bon.

Deux pipelines se recouvrent, il faut en fermer un. Lequel ?

- **celui de la demande de fusion** connaît la **cible** de la fusion. Il peut
  donc comparer, savoir ce qui a changé par rapport à la branche d'arrivée, et
  c'est lui qui s'affiche dans la demande ;
- **celui de la branche** ne sait rien de tout cela. Il ne voit qu'un commit
  sur une branche.

C'est donc le pipeline de **branche** qu'on ferme, et seulement quand une
demande de fusion est ouverte : sur une branche sans demande, il reste le seul
à pouvoir tourner.

## Le piège, et c'est tout le lab

**GitLab évalue les règles de haut en bas et s'arrête à la première qui
correspond.** Une règle qui refuse les pipelines de branche, placée avant celle
qui accepte la demande de fusion, fermera **aussi** la demande de fusion : un
pipeline de demande de fusion est aussi un pipeline sur une branche.

L'ordre n'est pas une préférence de style, c'est la logique du bloc.

## Ce que le lab vérifie

1. une **demande de fusion ouverte** existe, depuis une branche autre que la
   branche par défaut. Sans elle, le doublon ne peut pas se produire, donc rien
   ne peut être mesuré ;
2. sur le **dernier commit de cette branche**, il n'y a **qu'un** pipeline, et
   il vient de l'**événement de demande de fusion**.

## Un ordre à respecter, du côté des gestes aussi

La demande de fusion doit être **ouverte avant** le push que vous voulez
mesurer. Ouverte après, la variable que GitLab consulte pour savoir si une
demande existe est vide au moment où il évalue les règles, et le pipeline de
branche naît quand même.
