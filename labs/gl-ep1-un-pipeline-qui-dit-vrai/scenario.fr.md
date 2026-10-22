# Scénario

C'est l'épreuve de fin du niveau 1. Il n'y a pas de pas à pas, pas d'indice, et
les défauts ne sont pas nommés.

Le pipeline du projet est **vert**. Il tourne, il ne se plaint de rien, et
l'équipe s'y fie depuis des semaines.

Il ne garantit pourtant presque rien de ce qu'il affiche. Quatre promesses sont
faites par ce pipeline, et aucune n'est tenue :

1. « les tests passent » ;
2. « les résultats sont consultables » ;
3. « le jeton de déploiement est protégé » ;
4. « la production est maîtrisée ».

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Rendre le pipeline honnête : chacune de ces quatre promesses doit devenir
vraie, et vérifiable par quelqu'un qui n'a pas écrit le pipeline.

C'est le sens de l'épreuve, et c'est aussi la compétence du niveau : un
pipeline ne sert pas à être vert, il sert à **dire la vérité sur l'état du
code**. Un pipeline vert qui ne garantit rien est pire qu'un pipeline rouge,
parce que personne ne vient le regarder.

## Comment chercher

Vous avez tout vu dans les sept labs du niveau. Trois réflexes suffisent :

- **lire la configuration comme un relecteur**, pas comme son auteur : quelle
  promesse chaque job fait-il, et qu'est-ce qui l'empêcherait d'être fausse ?
- **demander à GitLab**, et non au fichier. Le linter CI du projet rend la
  configuration **compilée**, et l'API dit ce que le serveur a réellement
  produit : résultats de test, variables, pipelines par branche ;
- **essayer**. Une propriété de pipeline qui dépend d'une branche ne se lit
  pas, elle se mesure en poussant une branche.

## Ce que l'épreuve note

Elle note **l'état laissé dans la forge**, jamais les commandes tapées :

1. aucun job de test n'est autorisé à échouer, et ils ont réellement réussi ;
2. le rapport de test du pipeline n'est pas vide côté GitLab ;
3. aucune forme de secret ne subsiste dans la configuration compilée, et le
   projet porte au moins une variable **masquée** ;
4. une branche de travail poussée ne déclenche **aucun** job de déploiement.

## Ce que l'épreuve ne note pas

Ni le nom de votre variable, ni la façon dont vous protégez la production, ni
l'outil qui produit le rapport. Il y a plusieurs bonnes réponses, et une branche
de travail qui ne déclenche aucun pipeline du tout en est une.

## Un avertissement, parce qu'il compte

Le quatrième contrôle **pousse une branche** depuis la copie de travail de la
machine pour mesurer ce que la forge protège, puis la supprime. Si vous
travaillez vous-même sur une branche nommée `essai-de-l-epreuve`, renommez-la.
