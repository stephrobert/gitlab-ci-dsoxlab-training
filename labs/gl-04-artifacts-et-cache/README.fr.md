# Lab : cache des dépendances et rapport de tests

Un pipeline vert mais gaspilleur : chaque job réinstalle ses dépendances, et
les résultats de tests disparaissent avec le job. Distinguer le cache, qui
évite de refabriquer, de l'artefact, qui transmet un résultat.

Leçon compagnon :
[Artifacts et cache](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-04-artifacts-et-cache/).

```bash
dsoxlab run gl-04-artifacts-et-cache
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-04/pipeline-craft (branche main).
dsoxlab challenge gl-04-artifacts-et-cache
dsoxlab check gl-04-artifacts-et-cache
```

La note lit le rapport de tests du pipeline et les journaux des jobs : un
artefact déclaré par son seul chemin ne remplit pas l'onglet Tests, et un
cache ne prouve rien tant qu'il n'a pas été restauré.
