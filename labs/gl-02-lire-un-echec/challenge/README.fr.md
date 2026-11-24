# Lire un échec et le corriger

## La situation

Un collègue a poussé du code sur `pipeline-craft`, et **le pipeline est rouge**.
Personne ne comprend pourquoi. Le réflexe de l'équipe est de le relancer « au
cas où », ce qui ne corrige rien : un pipeline qui échoue pour une bonne raison
échouera à l'identique au second essai.

Trois erreurs ont été introduites, et elles ne se montrent pas en même temps.
La première empêche GitLab de créer le pipeline : tant qu'elle est là, **aucun
job ne tourne**, donc rien d'autre ne peut être signalé. Les deux suivantes
sont dans le code, et seul le journal d'un job les révèle.

Le projet est dans la forge du lab, avec son pipeline en échec. Une copie du
dépôt vous attend sur la machine.

## Mission

Remettez le pipeline au vert, en lisant les messages de GitLab plutôt qu'en
devinant.

Deux familles d'erreurs vous attendent, et les distinguer est tout l'enjeu :

- une erreur de **configuration CI**, que GitLab détecte **avant** de lancer le
  moindre job. Son symptôme est reconnaissable : un pipeline en échec qui ne
  contient **aucun job** ;
- des erreurs de **code**, que seul un job en échec révèle, dans son journal.

À la fin, le dernier pipeline de la branche par défaut doit être **vert**, et
les deux gestes, contrôle du style et suite de tests, doivent avoir réellement
tourné et réussi.

## Ce que le lab vérifie

La note porte sur l'état laissé sur la forge, et elle mesure les **trois
corrections**, pas seulement le vert final :

1. GitLab **accepte** la configuration, ce que son propre linter confirme ;
2. les deux imports inutiles ont disparu **du dépôt**, pas seulement de votre
   machine ;
3. le dernier pipeline de la branche par défaut est vert ;
4. les journaux des jobs réussis portent la trace du lint **et** des tests.

Le dernier point ferme un raccourci tentant : supprimer le job de lint rend le
pipeline vert sans avoir corrigé une seule ligne.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-02/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline est **rouge**. Trois erreurs y ont été introduites : une dans le
`.gitlab-ci.yml`, deux dans le code. Elles ne se montrent pas en même temps.

### Objectif (état attendu)

1. GitLab **accepte** la configuration du pipeline. Son linter, dans
   **Build > Pipeline editor**, le confirme sur la branche choisie.
2. Les deux imports inutiles ont disparu du dépôt, dans `app/main.py` et
   `app/routes/health.py`.
3. Le **dernier** pipeline de la branche par défaut est **vert**.
4. Les journaux des jobs réussis portent la trace du contrôle de style **et**
   de la suite de tests.

### La méthode, qui est le vrai sujet

- un pipeline en échec **sans aucun job** est un refus de configuration, pas
  une erreur d'exécution. Le message est à lire sur le pipeline lui-même, ou
  dans l'éditeur de pipeline ;
- le journal d'un job en échec se lit **par la fin** : la dernière ligne donne
  le code de sortie, et les lignes au-dessus le résumé de l'outil ;
- une erreur de ruff tient en deux lignes : le code de règle avec son message,
  puis la position sous la forme `fichier:ligne:colonne`.

### Validation

```bash
dsoxlab check gl-02-lire-un-echec
```
