# Scénario

C'est l'épreuve du niveau 3, celui qui s'appelle « Industrialiser ». Il n'y a ni
pas à pas, ni indice, et les défauts ne sont pas nommés.

Le projet `pipeline-craft` porte un pipeline vert. Un collègue l'a écrit vite,
il marche, et l'équipe veut maintenant le faire tourner pour dix autres projets.
Votre responsable technique pose quatre questions :

- **est-il écrit une fois, ou recopié ?**
- **combien de temps un changement attend-il, et quoi ?**
- **que se passe-t-il quand une étape échoue pour une raison qui n'est pas le code ?**
- **qu'est-ce qui empêche deux déploiements de tourner en même temps ?**

Une copie du dépôt vous attend sur la machine, et le projet est dans la forge du
lab. Les jobs n'exécutent que de petits scripts shell rangés dans `qa/` :
l'épreuve note la structure du pipeline, pas une application.

## Mission

Industrialiser le pipeline sans le casser : chaque changement doit laisser le
dernier pipeline de `main` au vert. Lisez le pipeline existant comme le ferait un
relecteur, trouvez ce qui n'est pas industriel, et corrigez-le.

Ce n'est pas le lab qui précède. Là vous construisiez depuis un cahier des
charges. Ici vous diagnostiquez un pipeline existant, et personne ne vous dit où
regarder.

## Ce que l'épreuve note

Elle note **l'état que la forge rapporte**, jamais les commandes tapées :

1. les parties communes sont écrites une fois (include ou `extends`) ;
2. les jobs forment un graphe, et un job démarre avant la fin de toute son étape ;
3. les tests s'exécutent en matrice, et chaque instance remonte un rapport de
   test non vide ;
4. un pipeline enfant construit depuis l'artefact d'un job s'exécute et réussit ;
5. le déploiement est verrouillé et borné, les relances sont limitées aux
   pannes système et un échec transitoire est absorbé ;
6. le dernier pipeline de `main` est vert et résulte de votre travail.

## Ce que l'épreuve ne note pas

Ni les noms de vos fichiers ou de vos jobs, ni le nombre de fichiers en lesquels
vous découpez la configuration. Le déclenchement entre projets est hors périmètre.
