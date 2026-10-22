# Scénario

Le pipeline de `pipeline-craft` est au point : découpé, factorisé, avec sa
matrice. Et tous ses jobs sont écrits d'avance, dans des fichiers versionnés.

Une demande arrive qui ne rentre pas dans ce moule : sur la branche par défaut,
l'équipe voudrait une vérification supplémentaire, et seulement là. On peut le
faire avec une règle, bien sûr. Mais la demande suivante sera « un job par
service modifié », et le nombre de services n'est pas connu quand on écrit le
fichier.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Faites écrire au pipeline une partie de lui-même.

Un **pipeline enfant** n'a pas besoin d'exister dans le dépôt : il est
**produit pendant l'exécution**, par un job, puis déclenché par un autre.

Trois pièces :

- un job qui **écrit** un fichier de pipeline et le publie en artefact ;
- un job qui le **déclenche**, en incluant cet artefact ;
- une **stratégie**, pour que le parent attende le résultat de son enfant.

## Le point qui décide tout : la stratégie

Sans `strategy:`, le job déclencheur passe au vert **dès que l'enfant est
lancé**, sans attendre son résultat. Le parent est alors vert quoi qu'il
arrive en aval, et le pipeline enfant devient décoratif.

Deux stratégies font attendre le parent, et elles ne se valent pas :

- **`mirror`** reflète l'état de l'enfant, quel qu'il soit. C'est celle que
  GitLab recommande, disponible depuis la version 18.2 ;
- **`depend`** attend aussi, mais compte comme **réussi** un enfant en échec
  dont un job porte `allow_failure: true`. Il masque donc exactement ce qu'on
  lui demande de surveiller. La documentation de GitLab écrit « not
  recommended, use mirror instead ».

L'instance de ce lab tourne en GitLab 19.5.1 : `mirror` y est disponible.

## Ce que le lab vérifie

1. un **pipeline enfant a tourné**, déclenché par un job du parent, et il a
   réussi ;
2. le **job déclencheur porte l'état de son enfant**, ce qui prouve que le
   parent attend et reflète.

Le second point accepte `mirror` comme `depend` : le lab mesure le
comportement, pas le mot-clé. Le corrigé, lui, utilise `mirror`.

## Où regarder

Un job qui déclenche un pipeline aval n'est pas un job ordinaire. GitLab
l'appelle **bridge** et le sert sur un endpoint à part :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/bridges" \
  | jq -r '.[] | {name, status, enfant: .downstream_pipeline.status}'
```

Le chercher dans la liste des jobs ne donnerait rien.
