# Lab : un changement, un pipeline

Une file de runner qui a doublé sans qu'aucun job ait été ajouté : chaque push
sur une branche avec demande de fusion ouverte produit deux pipelines pour le
même commit.

Leçon compagnon :
[Workflows](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-17-workflows/).

```bash
dsoxlab run gl-17-un-seul-pipeline-par-changement
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-17/pipeline-craft (branche main).
dsoxlab challenge gl-17-un-seul-pipeline-par-changement
dsoxlab check gl-17-un-seul-pipeline-par-changement
```

La note se prend en comptant les pipelines d'un seul commit : deux, c'est le
défaut ; un, de source `merge_request_event`, c'est le travail fait.
