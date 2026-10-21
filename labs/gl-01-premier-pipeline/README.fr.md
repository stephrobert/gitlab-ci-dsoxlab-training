# Lab : un premier pipeline qui contrôle, teste et construit

Faire exécuter par GitLab ce que votre machine fait déjà : le style du code, la
suite de tests et la construction de l'image, en étapes visibles et en vert.

Leçon compagnon :
[Votre premier pipeline](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-01-premier-pipeline/).

```bash
dsoxlab run gl-01-premier-pipeline
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-01/pipeline-craft (branche main).
dsoxlab challenge gl-01-premier-pipeline
dsoxlab check gl-01-premier-pipeline
```

La note porte sur le pipeline que le serveur a réellement joué, lu dans l'API
de GitLab : son état, ses jobs réussis, ses étapes et les journaux de ses
jobs. Ni le nom des jobs, ni le contenu du `.gitlab-ci.yml` n'entrent dans la
note.
