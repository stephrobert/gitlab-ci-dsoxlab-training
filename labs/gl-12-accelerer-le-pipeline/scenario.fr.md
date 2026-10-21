# Scénario

Le pipeline de `pipeline-craft` met sept minutes. Personne ne s'en plaint
vraiment, et tout le monde attend.

Deux gaspillages s'y cachent, et le premier est invisible. Le pipeline a bien
un cache : il est déclaré, il se crée à chaque passage, il occupe de l'espace
disque. Et il **ne sert qu'une fois**.

Sa clé vaut `$CI_COMMIT_SHA`. Les deux jobs d'un **même** pipeline partagent ce
SHA, donc la même clé : le second retrouve bien le cache du premier, et son
journal annonce fièrement une extraction réussie. Mais au commit suivant, le
SHA change : le cache du passage précédent existe toujours, sous un nom que
personne ne cherchera plus.

C'est ce qui rend le défaut si durable. Les journaux montrent un cache qui
fonctionne, parce qu'il fonctionne, à l'intérieur d'un pipeline. Ce qu'il ne
fait jamais, c'est traverser deux commits.

Le second se voit dans le graphe du pipeline : les jobs **font la queue**. Les
tests attendent la fin du lint, alors qu'ils n'en ont aucun besoin.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Faites gagner du temps au pipeline, en traitant les deux causes.

- **la clé du cache** décide de sa durée de vie. Une clé qui change à chaque
  commit rend le cache introuvable ; une clé dérivée du fichier de dépendances
  ne change que quand les dépendances changent, ce qui est exactement la bonne
  fréquence ;
- **l'ordre des étapes** est une contrainte, pas une fatalité. Un job peut en
  être libéré, et démarrer dès que le pipeline commence.

## Ce que le lab vérifie

1. la **clé du cache est la même** d'un pipeline à l'autre. Ce n'est pas la
   restauration qui est mesurée, puisqu'elle a déjà lieu au départ, mais la
   stabilité de la clé ;
2. deux jobs de **stages différents** se sont **chevauchés dans le temps**.

Les deux se lisent dans ce que le serveur a produit, pas dans votre fichier :
les clés dans les journaux des jobs, le chevauchement dans leurs horodatages.
L'API n'expose ni les clés déclarées ni les dépendances. Le point 1 demande
donc **deux passages** à comparer.

## Une mesure qui n'en est pas une

On ne vous demande pas de prouver une durée. Elle varie avec la charge de la
machine, et un pipeline plus rapide une fois ne prouve rien. Ce sont les deux
mécaniques qui font baisser la durée qui sont mesurées, pas la durée
elle-même.

## Deux jobs du même stage ne comptent pas

Ils tournent déjà ensemble, sans que personne ait rien décidé. Le lab compare
donc des jobs de stages **différents** : c'est là que l'ordre par défaut
s'applique, et donc là qu'une décision se voit.
