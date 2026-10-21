# Scénario

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
