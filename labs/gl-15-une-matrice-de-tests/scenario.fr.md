# Scénario

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
