# Lab : la bonne image pour chaque job

Trois jobs sur une image Python complète, dont un qui tente de construire une
image Docker. Choisir l'image adaptée à chaque travail, et donner un démon au
job de construction.

Leçon compagnon :
[Images et runners](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-03-images-et-runners/).

```bash
dsoxlab run gl-03-images-et-runners
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-03/pipeline-craft (branche main).
dsoxlab challenge gl-03-images-et-runners
dsoxlab check gl-03-images-et-runners
```

La note se lit dans les journaux des jobs, où GitLab Runner inscrit l'image
qu'il a tirée : pipeline vert, `docker build` mené à bien, service Docker
démarré, et plus aucun job sur `python:3.12` complet.
