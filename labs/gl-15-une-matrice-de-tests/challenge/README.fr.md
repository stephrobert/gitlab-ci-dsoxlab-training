# Une matrice de tests

## La situation

Le pipeline de `pipeline-craft` est découpé, factorisé, rapide. Il teste sur
**une** version de Python, la 3.12, celle du poste de la personne qui a écrit
le job.

La production, elle, fait tourner deux versions : la 3.11 sur les serveurs
anciens, la 3.12 sur les neufs. Personne ne sait si le code marche encore sur
la première, et personne ne le saura avant la prochaine panne.

Par ailleurs, la suite complète prend du temps, et elle est lancée d'un bloc :
un test d'API en échec cache les résultats du reste.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Faites tester plusieurs combinaisons à la fois, et liez la construction à
toutes.

- **une matrice instancie le job**, une fois par combinaison. Deux versions de
  Python par deux suites de tests donnent quatre jobs, que GitLab nomme
  `pytest-matrix: [3.12-slim, core]` et compagnie, et qu'il lance en parallèle ;
- **la construction attend toutes les combinaisons**. Nommer le job de tests
  dans le `needs:` du build suffit : GitLab attend chacune de ses instances.
  Construire une image n'a de sens que si chaque combinaison passe.

## Le piège d'une matrice

Une matrice peut déclarer quatre combinaisons et lancer **quatre fois
exactement le même travail**. Le pipeline devient quatre fois plus coûteux et
n'apprend rien de plus. Ce que le lab vérifie, c'est donc que les combinaisons
**changent quelque chose** : les jobs doivent avoir tiré des images
différentes.

## Ce que le lab vérifie

1. la matrice a produit **au moins trois jobs** distincts, et ils ont réussi ;
2. les jobs ont tiré des **images différentes**, ce que leur journal inscrit,
   et les acquis tiennent : aucun job en échec, la couverture remonte.

## Une baisse de couverture qui n'est pas une régression

Chaque instance ne teste qu'une partie du code, donc chacune remonte une
couverture partielle, et GitLab en affiche la **moyenne**. Le chiffre baisse
par construction, sans qu'aucun test ait disparu. C'est le prix d'une matrice
qui découpe les suites, et il vaut mieux le savoir que le découvrir.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-15/pipeline-craft` sur la VM, sur la branche `main`.

Ses tests ne connaissent qu'une version de Python.

### Objectif (état attendu)

1. La matrice a produit **au moins trois jobs** distincts, tous réussis.
2. Ces jobs ont tiré des **images différentes**, aucun job n'a échoué, et la
   couverture remonte toujours.

### Ce que le dépôt fournit

`tests/` contient trois fichiers : `test_health.py`, `test_version.py` et
`test_items.py`. De quoi découper une suite « cœur » et une suite « api ».

### Deux rappels

- un `needs:` qui nomme un job de matrice attend **toutes** ses instances ;
- la couverture affichée **baisse** quand les suites sont découpées : GitLab
  fait la moyenne des instances. Ce n'est pas une régression.

### Validation

```bash
dsoxlab check gl-15-une-matrice-de-tests
```
