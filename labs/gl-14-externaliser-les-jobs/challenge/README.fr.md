# Challenge : un orchestrateur, et un fichier par étape

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-14/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline fait quatre-vingts lignes, et tout y est juste.

## Objectif (état attendu)

1. GitLab rapporte **au moins deux fichiers inclus**.
2. Le comportement n'a pas bougé : aucun job en échec, au moins quatre jobs
   réussis, et la couverture remonte toujours.
3. La configuration fusionnée porte encore `stages:` et `workflow:`.

## Deux choses à savoir

- les fichiers inclus **ne cloisonnent pas** : un job caché déclaré dans l'un
  est visible depuis l'autre, GitLab fusionnant tout avant d'évaluer ;
- une **ancre YAML** ne traverse pas les fichiers. Elle doit vivre dans le même
  fichier que son `<<:`.

## Vérifier ce que GitLab a inclus

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/ci/lint?dry_run=true&ref=main" \
  | jq '{valid, includes}'
```

Un `include:` mal écrit ne provoque pas toujours une erreur : il peut
simplement n'inclure personne.

## Validation

```bash
dsoxlab check gl-14-externaliser-les-jobs
```
