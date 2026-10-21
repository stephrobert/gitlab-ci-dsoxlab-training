# Lab : accélérer le pipeline

Un cache déclaré, créé à chaque passage, et qui ne sert qu'une fois : sa clé
change à chaque commit, donc il ne traverse jamais deux commits. Et des jobs
qui attendent une étape dont ils n'ont pas besoin.

Leçon compagnon :
[Accélérer le pipeline](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-12-accelerer-pipeline/).

```bash
dsoxlab run gl-12-accelerer-le-pipeline
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-12/pipeline-craft (branche main).
dsoxlab challenge gl-12-accelerer-le-pipeline
dsoxlab check gl-12-accelerer-le-pipeline
```

La note ne porte pas sur une durée, qui varie avec la charge de la machine :
elle porte sur les deux mécaniques qui la font baisser : une clé de cache
stable d'un pipeline à l'autre, et deux jobs qui se chevauchent dans le
temps.
