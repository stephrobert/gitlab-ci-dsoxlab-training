# Lab : factoriser le pipeline

Deux jobs qui déclarent la même image et le même cache, mot pour mot. Les
factoriser avec un job caché et une ancre, sans rien changer au comportement.

Leçon compagnon :
[extends et anchors](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-13-extends-anchors/).

```bash
dsoxlab run gl-13-factoriser-le-yaml
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-13/pipeline-craft (branche main).
dsoxlab challenge gl-13-factoriser-le-yaml
dsoxlab check gl-13-factoriser-le-yaml
```

C'est le seul lab de la série dont la note lit le fichier, et c'est assumé :
`extends` et les ancres sont résolus avant l'exécution, donc la factorisation
ne laisse aucune trace dans l'état. Le second test, lui, vérifie que le
comportement n'a pas bougé.
