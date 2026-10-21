# Challenge : publier l'image, et la garder traçable

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-09/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline construit une image et la jette. Le registre du projet est vide.

## Objectif (état attendu)

1. Le registre du projet porte **au moins une image**.
2. Un tag publié porte le **SHA court du dernier commit**.
3. Le journal d'un job réussi montre l'envoi.
4. Aucun job n'a échoué.

## Les variables que GitLab fournit

| Variable | Ce qu'elle contient |
|---|---|
| `$CI_REGISTRY` | l'adresse du registre de l'instance |
| `$CI_REGISTRY_IMAGE` | le chemin complet de l'image de ce projet |
| `$CI_REGISTRY_USER` et `$CI_REGISTRY_PASSWORD` | des identifiants jetables, valables le temps du job |
| `$CI_COMMIT_SHORT_SHA` | le SHA court du commit qui a déclenché le pipeline |

Vérifier le résultat, depuis la VM :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/registry/repositories?tags=true" \
  | jq '.[] | {path, tags: [.tags[].name]}'
```

L'interface montre la même chose sous **Deploy > Container Registry**.

## Validation

```bash
dsoxlab check gl-09-publier-au-registre
```
