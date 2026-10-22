# Challenge : un changement, un pipeline

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-17/pipeline-craft` sur la VM, sur la branche `main`.

Une branche qui porte une demande de fusion ouverte lance deux pipelines pour
le même commit.

## Objectif (état attendu)

1. Une **demande de fusion ouverte** existe, depuis une branche autre que la
   branche par défaut.
2. Sur le **dernier commit de cette branche**, il n'y a **qu'un** pipeline, et
   sa source est `merge_request_event`.

## Les trois gestes

1. corriger le `workflow:` ;
2. pousser une branche et **ouvrir la demande de fusion** ;
3. pousser un commit **après** l'ouverture : c'est celui-là qui se mesure.

## Deux rappels

- GitLab s'arrête à la **première règle** qui correspond. Une règle de refus
  placée trop haut ferme aussi la demande de fusion ;
- la demande doit être ouverte **avant** le push mesuré, sinon la variable que
  GitLab consulte est vide quand il évalue les règles.

## Compter les pipelines d'un commit

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
SHA=$(git rev-parse HEAD)
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?sha=$SHA" \
  | jq -r '.[] | "\(.id) \(.source) \(.status)"'
```

## Validation

```bash
dsoxlab check gl-17-un-seul-pipeline-par-changement
```
