# Challenge : faire dire au pipeline ce qu'il couvre

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-10/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline publie le rapport de tests, et rien sur la couverture.

## Objectif (état attendu)

1. Une **couverture** non nulle est arrivée à GitLab.
2. Un **rapport de couverture** est publié en artefact, le rapport de tests est
   toujours rempli, et aucun job n'a échoué.

## Ce que le dépôt fournit déjà

`requirements-dev.txt` installe **pytest-cov** : l'outil est là, il n'est pas
branché. Le paquet à couvrir est `app`.

Vérifier que la pêche a pris, depuis la VM :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID" | jq '{coverage}'
```

Un `null` veut dire que l'expression régulière n'a rien trouvé, sans que rien
n'ait échoué.

## Validation

```bash
dsoxlab check gl-10-rapports-de-qualite
```
