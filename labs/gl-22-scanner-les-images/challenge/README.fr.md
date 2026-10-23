# Challenge : scanner l'image, et cesser de livrer une faille critique

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-22/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline publie l'image dans le registre du projet et ne la scanne jamais.
Elle porte pourtant une vulnérabilité critique.

## Objectif (état attendu)

1. Le dernier pipeline de `main` porte un job de scan, et **son rapport JSON de
   Trivy** est conservé dans les artefacts.
2. Ce rapport porte sur l'**image de ce projet, au tag du commit**.
3. Un pipeline a **échoué à cause d'une critique**, rapport conservé, sans
   aucun déploiement.
4. `.trivyignore` écarte **le finding trié par l'équipe sécurité, et lui
   seul**, avec sa **raison** écrite au-dessus.
5. Le dernier rapport **ne liste plus** ce finding.

## À lire avant de commencer

Deux notes attendent à côté de la copie du dépôt, dans `/opt/dsoxlab/gl-22` :

- `REGISTRE-DU-LAB.txt` : le registre répond en HTTP et le projet est privé ;
- `NOTE-EQUIPE-SECURITE.txt` : le finding écarté, et pourquoi.

## Image de Trivy

`aquasec/trivy:0.58.1@sha256:ab70a02200597efa04748f210f793936eb647cbcdb0ea69cc30b226d6f5a22c7`, qui déclare un point d'entrée à neutraliser
(`entrypoint: [""]`) pour que GitLab puisse lancer le script du job.

## Quatre rappels

- une étape nouvelle se **déclare** dans `stages:`, sinon GitLab refuse toute la
  configuration et le pipeline naît `failed` sans un seul job ;
- un job en échec ne conserve **pas** ses artefacts sans `when: always` ;
- une exception se **justifie** à côté de l'identifiant, et ne couvre que le
  finding trié ;
- un pipeline rouge à la fin est normal tant que d'autres critiques subsistent.

## Validation

```bash
dsoxlab check gl-22-scanner-les-images
```
