# Challenge : faire sortir le secret du dépôt

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-05/pipeline-craft` sur la VM, sur la branche `main`.

Un mot de passe de base de données y traîne en clair, à deux endroits, et un
job l'affiche dans son journal.

## Objectif (état attendu)

1. Le secret a disparu du dépôt, dans `app/config.py` **et** dans
   `.gitlab-ci.yml`.
2. Le projet porte une variable CI/CD **masquée**, et **protégée** si la
   branche par défaut l'est.
3. Le secret n'apparaît dans **aucun journal** du dernier pipeline.

## Deux pièges

- GitLab **refuse de masquer** une valeur qui contient certains caractères :
  une URL complète de base de données en porte. Déclarez le **secret seul**,
  pas l'adresse ;
- une variable **protégée** n'est remise qu'aux branches et étiquettes
  protégées. Si votre branche de travail ne l'est pas, le job la recevra vide.

## Validation

```bash
dsoxlab check gl-05-sortir-les-secrets
```
