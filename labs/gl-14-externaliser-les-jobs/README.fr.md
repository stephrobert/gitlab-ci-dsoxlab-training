# Lab : un orchestrateur, et un fichier par étape

Un pipeline juste et long de quatre-vingts lignes, que plus personne ne lit en
entier. Sortir les jobs dans des fichiers inclus, et garder au centre ce qui
dit l'ordre et le déclenchement.

Leçon compagnon :
[Templates et include](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-14-templates-include/).

```bash
dsoxlab run gl-14-externaliser-les-jobs
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-14/pipeline-craft (branche main).
dsoxlab challenge gl-14-externaliser-les-jobs
dsoxlab check gl-14-externaliser-les-jobs
```

La note revient du côté du serveur : GitLab nomme lui-même les fichiers qu'il
a inclus, là où la factorisation du lab précédent ne laissait aucune trace.
