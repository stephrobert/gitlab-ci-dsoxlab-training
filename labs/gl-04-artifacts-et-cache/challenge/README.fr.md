# Challenge : cache et rapport de tests

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-04/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline est vert, mais chaque job réinstalle ses dépendances et les
résultats de tests ne sont lisibles que dans les journaux.

## Objectif (état attendu)

1. Le **dernier** pipeline de la branche par défaut est **vert**.
2. Le **rapport de tests du pipeline** est rempli, sans échec. Visible dans
   l'onglet **Tests** du pipeline.
3. Un cache a été **créé**.
4. Un cache a été **restauré** au moins une fois, ce qui demande un **second
   passage** du pipeline.

## Ce qui n'est pas imposé

Ni le nom des jobs, ni la clé du cache, ni le chemin mis en cache. Mettre en
cache le répertoire de pip par un autre chemin convient tout autant.

## Validation

```bash
dsoxlab check gl-04-artifacts-et-cache
```
