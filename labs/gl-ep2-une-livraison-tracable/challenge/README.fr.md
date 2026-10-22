# Épreuve : une livraison qu'on peut retracer

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-ep2/pipeline-craft` sur la VM, sur la branche `main`.

La chaîne construit, teste et déploie sans laisser de trace. Quatre traces
manquent, et l'une d'elles bloque les autres.

## Objectif (état attendu)

1. aucun job du dernier pipeline de `main` n'est en attente, et aucun n'a
   échoué ;
2. le projet porte au moins un **environnement**, et au moins un
   **déploiement réussi** y est enregistré ;
3. le **registre** du projet porte au moins une étiquette ;
4. aucun job de production n'est parti de lui-même sur la branche par défaut.

## Aucun indice n'est fourni

C'est une épreuve : les quatre défauts ne sont pas nommés, et il n'y a pas
d'indice à débloquer. Vous avez tout vu dans les quatre labs du niveau.

## Une contrainte de cet environnement

Le registre de cette forge répond en **HTTP**, pas en HTTPS. Un client Docker
refuse par défaut de parler à un registre en clair : le service Docker du job
doit déclarer l'adresse du registre comme non sécurisée. Le pipeline de départ
le fait déjà, c'est un acquis et non un défaut.

## Les commandes qui servent à vérifier

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft

# L'état réel des jobs du dernier pipeline
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/jobs" \
  | jq -r '.[] | "\(.name) \(.status)"'

# Ce que les runners du projet offrent, à comparer avec ce que les jobs demandent
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/runners" \
  | jq -r '.[] | "\(.description) \(.tag_list // [])"'

# Les environnements et les déploiements enregistrés
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/environments" | jq -r '.[] | "\(.name) \(.state)"'
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/deployments" \
  | jq -r '.[] | "\(.environment.name) \(.status) \(.ref)"'

# Les images publiées
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/registry/repositories" | jq -r '.[].id'
```

## Validation

```bash
dsoxlab check gl-ep2-une-livraison-tracable
```
