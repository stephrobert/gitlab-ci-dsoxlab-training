# Lab : des secrets qui se renouvellent sans casser le pipeline

Un pipeline vert qui utilise un jeton ni protégé ni masqué, et une clé SSH recopiée à
la main dans un fichier. Vous protégez et masquez le jeton, vous passez la clé en
variable de type fichier, puis vous renouvelez le jeton sans interrompre le
service : le nouveau d'abord, la preuve par un pipeline, la révocation de l'ancien
ensuite.

Leçon compagnon :
[Gestion des secrets dans GitLab CI](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/securite/secrets/).

```bash
dsoxlab run gl-20-secrets-avances
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-20/pipeline-craft (branche main).
dsoxlab challenge gl-20-secrets-avances
dsoxlab check gl-20-secrets-avances
```

La note se prend sur l'état que la forge porte : réglages des variables, jetons
d'accès actifs ou révoqués, jobs exécutés, journaux. Un `.gitlab-ci.yml` qui
parle d'une variable protégée ne prouve pas qu'elle l'est.

## Ce que vous saurez faire

- protéger et masquer une variable CI/CD, et dire ce que chaque réglage change ;
- passer un secret multi-lignes en variable de type fichier et adapter le job ;
- renouveler un secret sans interruption : créer le nouveau, le mettre en service,
  le prouver, puis révoquer l'ancien.

Ce lab n'exige ni Vault, ni service payant, ni édition Premium ou Ultimate de
GitLab : les jetons d'accès de projet existent en Community Edition.
