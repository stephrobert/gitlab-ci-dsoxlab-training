# Challenge : une matrice de tests

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-15/pipeline-craft` sur la VM, sur la branche `main`.

Ses tests ne connaissent qu'une version de Python.

## Objectif (état attendu)

1. La matrice a produit **au moins trois jobs** distincts, tous réussis.
2. Ces jobs ont tiré des **images différentes**, aucun job n'a échoué, et la
   couverture remonte toujours.

## Ce que le dépôt fournit

`tests/` contient trois fichiers : `test_health.py`, `test_version.py` et
`test_items.py`. De quoi découper une suite « cœur » et une suite « api ».

## Deux rappels

- un `needs:` qui nomme un job de matrice attend **toutes** ses instances ;
- la couverture affichée **baisse** quand les suites sont découpées : GitLab
  fait la moyenne des instances. Ce n'est pas une régression.

## Validation

```bash
dsoxlab check gl-15-une-matrice-de-tests
```
