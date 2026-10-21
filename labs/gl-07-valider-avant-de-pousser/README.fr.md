# Lab : valider avant de pousser

Un pipeline refusé, un défaut que le refus masque, et un troisième que GitLab
accepte sans rien dire. Les trouver sans pousser pour voir.

Leçon compagnon :
[Valider un pipeline](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-07-valider-pipeline/).

```bash
dsoxlab run gl-07-valider-avant-de-pousser
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-07/pipeline-craft (branche main).
dsoxlab challenge gl-07-valider-avant-de-pousser
dsoxlab check gl-07-valider-avant-de-pousser
```

La note lit la configuration que GitLab a acceptée et les jobs qui ont tourné.
Elle ne mesure pas la méthode : l'état final d'une personne méthodique et celui
d'une personne qui a tâtonné sont identiques.
