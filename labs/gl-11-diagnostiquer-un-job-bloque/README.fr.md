# Lab : deux pannes muettes

Un push qui ne produit aucun pipeline, puis un job qui attend indéfiniment sans
échouer. Deux pannes sans message, les plus coûteuses à diagnostiquer.

Leçon compagnon :
[Déboguer un job bloqué](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-11-debugger-job-bloque/).

```bash
dsoxlab run gl-11-diagnostiquer-un-job-bloque
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-11/pipeline-craft (branche main).
dsoxlab challenge gl-11-diagnostiquer-un-job-bloque
dsoxlab check gl-11-diagnostiquer-un-job-bloque
```

La note lit le pipeline laissé sur la forge : son existence d'abord, puis
l'absence de job en attente et la trace du linter. Un job `manual` n'est pas
un job bloqué.
