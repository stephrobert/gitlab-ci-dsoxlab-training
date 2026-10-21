# Lab : décider quand le pipeline tourne, et qui déploie

Tous les jobs tournent à chaque push, et rien n'est déployé. Poser un
`workflow:` global, des `rules:` par job, un déploiement automatique en recette
et un déploiement manuel en production.

Leçon compagnon :
[Contrôler l'exécution](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-06-controler-execution/).

```bash
dsoxlab run gl-06-controler-execution
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-06/pipeline-craft (branche main).
dsoxlab challenge gl-06-controler-execution
dsoxlab check gl-06-controler-execution
```

La note lit l'état du pipeline : un déploiement réussi, un déploiement en
attente de décision, le vert conservé. Le bloc `workflow:` est le seul point
lu dans la configuration que GitLab a comprise, faute d'effet observable sans
pousser une branche.
