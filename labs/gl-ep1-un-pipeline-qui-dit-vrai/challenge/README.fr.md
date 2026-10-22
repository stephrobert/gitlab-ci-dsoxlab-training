# Épreuve : un pipeline qui dit vrai

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-ep1/pipeline-craft` sur la VM, sur la branche `main`.

Le pipeline est vert. Il fait quatre promesses et n'en tient aucune. À vous de
trouver lesquelles, et de les rendre vraies.

## Objectif (état attendu)

1. aucun job de test n'est autorisé à échouer, et ils ont réellement réussi ;
2. le rapport de test du pipeline n'est pas vide côté GitLab ;
3. aucun secret ne subsiste dans la configuration compilée, et le projet porte
   au moins une variable **masquée** ;
4. une branche de travail poussée ne déclenche aucun job de déploiement.

## Aucun indice n'est fourni

C'est une épreuve : les quatre défauts ne sont pas nommés, et il n'y a pas
d'indice à débloquer. Vous avez tout vu dans les sept labs du niveau.

## Les commandes qui servent à vérifier

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft

# Ce que GitLab a compris de votre configuration, héritages résolus
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/ci/lint?dry_run=true&ref=main" \
  | jq -r '.valid, .errors[]?'

# Les résultats de test tels que le serveur les voit
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/test_report" \
  | jq '{total_count, failed_count}'

# Les variables du projet, et leur masquage
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/variables" \
  | jq -r '.[] | "\(.key) masked=\(.masked)"'

# Ce qu'une branche déclenche réellement
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=<branche>" \
  | jq -r '.[0].id'
```

## Validation

```bash
dsoxlab check gl-ep1-un-pipeline-qui-dit-vrai
```
