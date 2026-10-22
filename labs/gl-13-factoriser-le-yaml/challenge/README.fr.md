# Challenge : factoriser le pipeline

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-13/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline marche et se répète.

## Objectif (état attendu)

1. Le fichier porte un **job caché** étendu par au moins un job, et une
   **ancre YAML** fusionnée par `<<:`.
2. Le comportement **n'a pas changé** : aucun job en échec, au moins quatre
   jobs réussis, et la couverture remonte toujours.

## Ce qui n'est pas imposé

Ni le nom du job caché, ni celui de l'ancre, ni leur nombre. Deux jobs cachés
et trois ancres conviennent autant qu'un de chaque.

## Deux rappels

- `extends:` fusionne **en profondeur** : un job peut hériter d'un cache et
  n'en redéclarer que la politique ;
- `coverage:` appartient au **job**. Le perdre en déplaçant le job de tests
  laisse le pipeline vert et la couverture vide.

## Validation

```bash
dsoxlab check gl-13-factoriser-le-yaml
```
