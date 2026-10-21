# Scénario

Le pipeline de `pipeline-craft` construit une image Docker à chaque passage sur
la branche par défaut. Puis le job se termine, et l'image disparaît avec lui.

Personne ne peut la déployer : il faudrait la reconstruire, en espérant obtenir
la même. Et quand la recette tombe en panne, personne ne peut dire quelle
version tourne, parce qu'aucune image n'a de nom durable.

La forge du lab a un **registre de conteneurs**, et il est vide.

Le projet est dans la forge. Une copie du dépôt vous attend sur la machine.

## Mission

Publiez l'image depuis le pipeline, sous un nom qui désigne le code qu'elle
contient.

Deux idées, et la seconde est celle qui compte :

- **publier**, c'est s'authentifier puis pousser. GitLab fournit au job tout ce
  qu'il faut : l'adresse du registre, un identifiant et un mot de passe
  jetables, et le chemin complet de l'image du projet. Trois variables
  `CI_REGISTRY_*` à connaître ;
- **rester traçable**, c'est nommer l'image d'après le **commit**. Un tag qui
  désigne un commit précis permet de dire, six mois plus tard, quel code tourne
  en production. Un tag mobile ne le permet pas.

## Une particularité de la forge du lab

Le registre de ce GitLab écoute en **HTTP**. Le service Docker du job en est
informé par une option, posée pour vous dans l'état de départ. Sur gitlab.com,
en HTTPS, la question ne se pose pas.

## Ce que le lab vérifie

1. le registre du projet porte **au moins une image** ;
2. un tag publié porte le **SHA court du dernier commit** de la branche par
   défaut ;
3. le journal d'un job réussi montre que c'est **le pipeline** qui a publié,
   pas une main sur un clavier ;
4. aucun job du pipeline n'a échoué.

Le point 2 est le cœur du lab. Un préfixe ou un suffixe autour du SHA ne gêne
pas : `sha-1a2b3c4d` convient autant que `1a2b3c4d`. Ce qui est refusé, c'est
qu'aucun tag ne désigne le commit.

## Sur le tag `latest`

Vous pouvez en publier un, le lab l'accepte. Il ne l'exige pas, et ce n'est pas
un oubli : un tag mobile invite celui qui consomme l'image à prendre une
référence qui bouge sous ses pieds. Le tag du commit, lui, dit toujours la même
chose.
