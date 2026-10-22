# Challenge : reconstruire tout le pipeline

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-19/pipeline-craft` sur la VM, sur la branche `main`.

Le dépôt n'a **aucun fichier de CI**. Le cahier des charges est dans
`CAPSTONE-LAB-19.md`, à la racine du dépôt.

## Objectif (état attendu)

1. un pipeline tourne sur la branche par défaut, **sans job en échec**, et ses
   **cinq étapes** portent des jobs : analyse, test, orchestration,
   construction, déploiement ;
2. GitLab a **inclus au moins deux fichiers locaux** : la CI est modulaire ;
3. la **matrice** produit au moins deux instances, dont une en Python 3.11 et
   une en 3.12, et le **rapport de test** du pipeline n'est pas vide ;
4. un **pipeline enfant** a été déclenché depuis un artefact, et il ne s'est
   pas terminé en échec ;
5. le **registre** du projet porte au moins une étiquette ;
6. la forge porte au moins un **verrou de déploiement**, les déploiements
   portent un **délai**, et **aucune relance** ne couvre un échec de script.

## Avant de commencer : le registre de cet environnement

Il répond en HTTP. Le mémo `/opt/dsoxlab/gl-19/REGISTRE-DU-LAB.txt` donne la
ligne à écrire pour que le service Docker du job accepte de lui parler.

## Les quatre commandes qui servent à vérifier

Demander à GitLab ce qu'il a compris de votre configuration, et ce qu'il a
inclus :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/ci/lint?dry_run=true&ref=main" \
  | jq -r '.valid, .errors[]?, (.includes[]?.location)'
```

Lire le rapport de test du dernier pipeline, qui reste vide si le rapport JUnit
n'est pas déclaré comme tel :

```bash
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/test_report" \
  | jq '{total_count, failed_count}'
```

Trouver le pipeline enfant, que GitLab ne sert **pas** parmi les jobs :

```bash
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/bridges" \
  | jq -r '.[] | "\(.name) \(.status) enfant=\(.downstream_pipeline.status // "aucun")"'
```

Compter les verrous de déploiement et les étiquettes publiées :

```bash
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/resource_groups" | jq -r '.[].key'
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/registry/repositories" | jq -r '.[].id'
```

## Validation

```bash
dsoxlab check gl-19-reconstruire-tout-le-pipeline
```
