# Challenge : accélérer le pipeline

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-12/pipeline-craft` sur la VM, sur la branche `main`.

Son cache n'est jamais relu, et ses jobs font la queue.

## Objectif (état attendu)

1. La **clé du cache** est la même d'un pipeline à l'autre.
2. Deux jobs de **stages différents** se sont **chevauchés dans le temps**.

## Deux rappels

- la clé se compare entre **deux** passages : relancez le pipeline après
  votre correction. Et attention, un cache restauré ne prouve rien ici : avec
  une clé en `$CI_COMMIT_SHA`, les deux jobs d'un même pipeline la partagent
  déjà ;
- deux jobs du même stage tournent déjà ensemble. Le lab compare des stages
  **différents**.

## Vérifier le chevauchement

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/jobs" \
  | jq -r '.[] | "\(.name) [\(.stage)] \(.started_at) -> \(.finished_at)"'
```

## Validation

```bash
dsoxlab check gl-12-accelerer-le-pipeline
```
