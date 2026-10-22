# Lab : activer les scanners, et lire ce qu'ils disent

Un pipeline vert qui ne regarde que les tests, et un secret écrit dans le code
que personne n'a jamais vu. Vous activez SAST et Secret Detection, vous lisez
leurs rapports JSON, et vous corrigez ce qu'ils désignent.

Leçon compagnon :
[Scanners de sécurité](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/fondamentaux/securite-scanners/).

```bash
dsoxlab run gl-21-activer-les-scanners
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-21/pipeline-craft (branche main).
dsoxlab challenge gl-21-activer-les-scanners
dsoxlab check gl-21-activer-les-scanners
```

Ce lab tourne sur GitLab **Community Edition** : il ne fait pratiquer que les
fonctions de cette édition. Le Security Dashboard, les rapports de
vulnérabilités du projet et les merge request approval policies sont des
fonctions Ultimate, et n'y sont pas utilisés. On lit les rapports en fichiers.

La note se prend sur les jobs que la forge a réellement exécutés et sur les
rapports qu'ils ont déposés, jamais sur le contenu de `.gitlab-ci.yml` : un
template inclus qui n'a pas tourné ne vaut rien. Les runners ont besoin d'un
accès à internet pour télécharger les images des scanners.
