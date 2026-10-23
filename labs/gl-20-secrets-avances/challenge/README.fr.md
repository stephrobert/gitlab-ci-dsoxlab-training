# Challenge : des secrets protégés, en fichier, et renouvelés

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-20/pipeline-craft` sur la VM, sur la branche `main` (protégée).

Deux jobs, `joindre-le-service` et `installer-la-cle`, consomment les variables
`SERVICE_TOKEN` et `DEPLOY_KEY`. Les deux sont mal gérées.

## Objectif (état attendu)

1. `SERVICE_TOKEN` est **protégée** et **masquée**.
2. `DEPLOY_KEY` est une variable de **type fichier**, **protégée**, de valeur
   inchangée.
3. Le jeton `service-v1` est **révoqué**. `SERVICE_TOKEN` porte un **autre**
   jeton valide, et `joindre-le-service` n'a jamais échoué depuis le départ.
4. Le dernier pipeline de `main` est sain, les deux jobs passent, et le
   journal de `installer-la-cle` affiche `CLE-SOURCE=fichier` (ligne du job de
   départ, à conserver).

## À lire avant de commencer

`NOTE-SECRETS.txt`, à côté de la copie du dépôt dans `/opt/dsoxlab/gl-20`.

## Quatre rappels

- une variable de type fichier met dans la variable le **chemin** d'un fichier,
  pas la valeur : le job doit lire ce fichier ;
- changer le type de la variable sans adapter le job casse le pipeline : les deux
  changements vont ensemble ;
- un job qui échoue après le changement de type de `DEPLOY_KEY` n'est pas une
  panne de la forge : il lit encore la valeur là où il reçoit un chemin ;
- la route `rotate` de l'API crée le nouveau jeton et révoque l'ancien d'un seul
  geste : il n'y a alors aucun temps pour mettre le nouveau en service.

## Validation

```bash
dsoxlab check gl-20-secrets-avances
```
