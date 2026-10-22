# Challenge : un pipeline enfant

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-16/pipeline-craft` sur la VM, sur la branche `main`.

Tous ses jobs sont écrits d'avance.

## Objectif (état attendu)

1. Un **pipeline enfant a tourné** et réussi, déclenché par un job du parent.
2. Le **job déclencheur porte l'état de son enfant**, et aucun job du parent
   n'a échoué.

## Les trois pièces

- un job qui écrit un fichier de pipeline et le publie en **artefact** ;
- un job qui le déclenche, par `trigger: include: - artifact: … job: …` ;
- une **stratégie** : `mirror` de préférence, `depend` accepté.

## Deux rappels

- sans `strategy:`, le parent passe au vert dès que l'enfant est **lancé** ;
- un job de déclenchement se lit sur `/pipelines/:id/bridges`, pas dans la
  liste des jobs.

## Validation

```bash
dsoxlab check gl-16-un-pipeline-enfant
```
