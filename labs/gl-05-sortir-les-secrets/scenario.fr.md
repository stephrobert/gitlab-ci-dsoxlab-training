# Scénario

Le pipeline de `pipeline-craft` est **vert**, et il le restera quoi que vous
fassiez. C'est précisément le problème : un secret en clair ne casse rien, il
fuit.

Un mot de passe de base de données traîne à **deux endroits** dans le dépôt :

- dans `app/config.py`, en **valeur de repli** de la lecture d'environnement.
  Pratique quand on développe, et commité pour toujours ;
- dans `.gitlab-ci.yml`, en **variable de pipeline**, que le job de tests
  **affiche dans son journal** par un `echo`.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Faites sortir ce secret du dépôt et des journaux, sans casser le pipeline.

Trois gestes, et le troisième est celui qu'on oublie :

- **retirer** le secret des deux fichiers. Une valeur de repli ne porte jamais
  de secret : une base de développement locale suffit ;
- **le déclarer dans la forge**, sous `Settings > CI/CD > Variables`. Deux
  réglages comptent : **masquée**, pour que la valeur n'apparaisse pas dans un
  journal, et **protégée**, pour qu'elle ne soit remise qu'aux branches et
  étiquettes protégées ;
- **vérifier** que le secret n'apparaît plus dans les journaux. Un journal se
  télécharge, par quiconque voit le projet.

## Ce que le lab vérifie

1. le secret a disparu du dépôt, dans `app/config.py` **et** dans
   `.gitlab-ci.yml` ;
2. une variable CI/CD existe, **masquée**, et **protégée** si la branche par
   défaut l'est ;
3. le secret n'apparaît dans **aucun journal** du dernier pipeline.

Aucun test ne vérifie que le pipeline est vert : il l'était déjà avant votre
travail, et un test qui passe sans rien mesurer n'est pas un test.

## Une limite à connaître

Retirer un secret de la branche par défaut ne l'efface pas de l'**historique**
Git. Dans la vraie vie, un secret commité est un secret **à renouveler** : on
change la valeur, on ne compte pas sur son retrait. Le lab s'arrête au geste
qui se mesure, mais la règle, elle, ne s'arrête pas là.
