# Lab : lire un échec de pipeline et le corriger

Un pipeline rouge, trois bugs, et leurs indices dans les messages de GitLab.
Diagnostiquer avant de corriger, au lieu de relancer « au cas où ».

Leçon compagnon :
[Lire un échec et le corriger](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-02-lire-un-echec/).

```bash
dsoxlab run gl-02-lire-un-echec
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-02/pipeline-craft (branche main).
dsoxlab challenge gl-02-lire-un-echec
dsoxlab check gl-02-lire-un-echec
```

La note mesure les **trois corrections**, pas seulement le vert final :
configuration acceptée par GitLab, imports inutiles disparus du dépôt,
pipeline vert, et trace du lint comme des tests dans les journaux.
