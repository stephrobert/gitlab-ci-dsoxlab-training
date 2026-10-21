# Challenge : valider avant de pousser

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-07/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline est rouge **sans aucun job** : la configuration est refusée.

## Objectif (état attendu)

1. GitLab **accepte** la configuration.
2. Plus aucun motif à **trois étoiles** dans la configuration fusionnée.
3. Le job de tests a **tourné et réussi**.
4. **Aucun job du pipeline n'a échoué.** Son statut sera **`manual`** :
   le déploiement de production attend sa décision.

## Valider sans pousser

```bash
# Depuis la VM, l'API de lint sur la branche choisie :
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/ci/lint?dry_run=true&ref=main" \
  | jq '{valid, errors}'
```

L'éditeur de pipeline (`Build > Pipeline editor`) dit la même chose dans
l'interface, et la réponse de l'API porte en plus `merged_yaml`, la
configuration que GitLab a réellement comprise.

## Validation

```bash
dsoxlab check gl-07-valider-avant-de-pousser
```
