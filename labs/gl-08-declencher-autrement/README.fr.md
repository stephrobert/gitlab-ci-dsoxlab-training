# Lab : déclencher un pipeline sans pousser

Un pipeline qui ne sait réagir qu'à un push, une suite de régression à passer
la nuit, et une équipe voisine qui voudrait le relancer sans compte sur la
forge.

Leçon compagnon :
[Déclencher un pipeline](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-08-declencher-pipeline/).

```bash
dsoxlab run gl-08-declencher-autrement
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-08/pipeline-craft (branche main).
dsoxlab challenge gl-08-declencher-autrement
dsoxlab check gl-08-declencher-autrement
```

La note lit les planifications, les jetons de déclenchement et les pipelines
qui ont réellement tourné. Elle compare les jobs d'un pipeline hors push à
ceux d'un push : les règles d'un job ne sont pas exposées par l'API, et c'est
la seule façon de prouver qu'une règle de source fonctionne.
