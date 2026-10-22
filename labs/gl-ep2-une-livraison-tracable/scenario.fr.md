# Scénario

C'est l'épreuve de fin du niveau 2, celui qui s'appelle « Livrer ». Il n'y a
pas de pas à pas, pas d'indice, et les défauts ne sont pas nommés.

La chaîne de ce projet construit, teste et déploie. Elle ne laisse aucune
trace.

Personne ne peut répondre à ces questions, et pourtant elles se posent chaque
semaine :

- **qu'est-ce qui tourne en production, et depuis quand ?**
- **sur quelle image ce déploiement reposait-il ?**
- **qui a décidé de livrer ?**

Et un quatrième problème empêche de répondre aux trois premières : le pipeline
ne finit jamais.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Rendre la livraison **traçable** : quatre traces manquent, à vous de les
trouver et de les faire exister.

C'est la compétence du niveau, et elle est mal comprise. Livrer, ce n'est pas
copier des fichiers sur un serveur : c'est pouvoir dire, six mois plus tard,
quelle version tourne où, d'où elle vient, et qui l'a décidée. Un déploiement
qu'on ne peut pas retracer n'a pas eu lieu, du point de vue de l'équipe qui
devra le reprendre.

## Un défaut bloque les autres, commencez par là

Un job peut ne pas démarrer **sans pour autant échouer**. Il n'y a alors aucun
message, aucun journal, et le pipeline reste en cours indéfiniment : tout ce
qui vient après n'arrive jamais.

C'est la panne la plus désagréable de GitLab CI, parce qu'elle ne produit rien
à lire. Vous l'avez diagnostiquée dans un lab de ce niveau : le réflexe est de
comparer ce que le job **demande** avec ce que les runners du projet
**offrent**.

## Ce que l'épreuve note

Elle note **l'état laissé dans la forge**, jamais les commandes tapées :

1. aucun job du dernier pipeline n'est en attente, et aucun n'a échoué ;
2. le projet porte au moins un **environnement**, et au moins un
   **déploiement réussi** y est enregistré ;
3. le **registre** du projet porte au moins une étiquette ;
4. aucun job de production n'est parti de lui-même sur la branche par défaut.

## Ce que l'épreuve ne note pas

Ni le nom de vos environnements, ni leur URL, ni la façon dont vous protégez la
production. Pour ce dernier point, deux réponses conviennent et les deux sont
acceptées : le job attend une main humaine, ou il ne part que sur une étiquette
posée délibérément.
