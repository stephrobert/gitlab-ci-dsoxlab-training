# Lab : un pipeline qui écrit ses propres jobs

Un pipeline dont tous les jobs sont écrits d'avance, et une demande qui ne
rentre pas dans ce moule. Générer un pipeline enfant pendant l'exécution, le
déclencher, et faire attendre le parent.

Leçon compagnon :
[Pipelines dynamiques](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-16-pipelines-dynamiques/).

```bash
dsoxlab run gl-16-un-pipeline-enfant
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-16/pipeline-craft (branche main).
dsoxlab challenge gl-16-un-pipeline-enfant
dsoxlab check gl-16-un-pipeline-enfant
```

La note lit l'endpoint des ponts : un enfant qui a tourné, et un job
déclencheur qui porte son état. Sans stratégie, le parent passe au vert dès
que l'enfant est lancé, et l'enfant devient décoratif.
