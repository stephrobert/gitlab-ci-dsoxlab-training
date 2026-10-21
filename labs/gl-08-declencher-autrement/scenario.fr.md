# Scénario

Le pipeline de `pipeline-craft` fonctionne bien, et il ne sait faire qu'une
chose : réagir à un push. Deux besoins de l'équipe butent dessus.

Le premier est une **suite de régression complète**, qui prend quinze minutes.
La lancer à chaque push coûte cher et ne rapporte rien : personne n'attend son
résultat. Sa place est la nuit, quand la machine est libre.

Le second vient de l'extérieur. L'équipe qui publie le catalogue d'images
voudrait **relancer le pipeline** quand sa propre chaîne a fini. Elle n'a pas
de compte sur la forge, et n'en veut pas.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Faites naître le pipeline autrement que d'un push, et réservez un job à une
seule provenance.

Ce qu'il faut comprendre d'abord : **`$CI_PIPELINE_SOURCE` dit d'où vient le
pipeline**, et le bloc `workflow:` décide quelles provenances sont acceptées.
Une source absente de cette liste ne produit **aucun** pipeline, et rien ne le
signale : il n'y a simplement rien dans l'onglet.

Trois gestes :

- faire accepter au `workflow:` les sources `schedule`, `trigger` et `api` ;
- créer une **planification** active dans la forge, et un **jeton de
  déclenchement** pour l'équipe voisine ;
- réserver la suite de régression à la source `schedule`.

## Un piège de vocabulaire

`$CI_MERGE_REQUEST_IID` et `$CI_PIPELINE_SOURCE == "merge_request_event"` se
ressemblent et ne disent pas la même chose : la première existe aussi dans un
pipeline de branche rattaché à une demande de fusion. C'est la seconde qui
nomme la provenance.

## Ce que le lab vérifie

1. une **planification** existe et est **active** ;
2. un **jeton de déclenchement** existe ;
3. un pipeline a réellement tourné depuis une source **autre qu'un push**, et
   aucun de ses jobs n'a échoué ;
4. un job n'apparaît **que** dans le pipeline hors push, et pas dans celui du
   push.

Le point 4 demande donc les deux : un pipeline venu d'ailleurs, et un pipeline
de push à comparer. Les règles d'un job ne sont pas exposées par l'API : les
comparer est la seule façon de prouver qu'une règle de source fonctionne.

**Et une planification ne s'attend pas, elle se joue.** Le bouton de lecture de
`Build > Pipeline schedules`, ou `POST /pipeline_schedules/:id/play`, lance
immédiatement un pipeline qui porte bien la source `schedule`. Sans cela, il
faudrait attendre l'heure dite pour savoir si la règle fonctionne. Une
planification qu'on n'a jamais jouée est une planification qu'on n'a pas
vérifiée.

Vos tests ne liront jamais la **valeur** d'un jeton de déclenchement, seulement
son existence : un message d'échec qui la porterait la publierait.
