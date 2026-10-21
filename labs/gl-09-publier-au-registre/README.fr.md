# Lab : publier l'image, et la garder traçable

Une image construite à chaque passage et jetée avec son job. La publier depuis
le pipeline, sous un tag qui nomme le commit.

Leçon compagnon :
[Publier au registre](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-09-publier-registry/).

```bash
dsoxlab run gl-09-publier-au-registre
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-09/pipeline-craft (branche main).
dsoxlab challenge gl-09-publier-au-registre
dsoxlab check gl-09-publier-au-registre
```

La note lit le registre du projet, le tag publié et le journal du job. Le
cœur du lab est le tag : une image dont le nom ne désigne aucun commit ne se
relie pas au code qu'elle exécute.
