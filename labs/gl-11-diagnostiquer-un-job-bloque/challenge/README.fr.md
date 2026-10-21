# Challenge : deux pannes muettes

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-11/pipeline-craft` sur la VM, sur la branche `main`.

Vous poussez, et aucun pipeline n'apparaît. Derrière cette panne, une seconde
attend.

## Objectif (état attendu)

1. Un **pipeline existe** sur la branche par défaut.
2. **Aucun job n'est resté en attente**, le linter a tourné, aucun job n'a
   échoué.

## Deux rappels

- un job **`manual`** attend une décision humaine : il est sain, ce n'est pas
  lui qui bloque ;
- retirer un job du pipeline le fait disparaître des jobs bloqués sans rien
  réparer. Le lab vérifie que le linter a **réellement tourné**.

## Validation

```bash
dsoxlab check gl-11-diagnostiquer-un-job-bloque
```
