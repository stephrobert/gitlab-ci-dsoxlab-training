# Challenge : lire un échec et le corriger

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-02/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline est **rouge**. Trois erreurs y ont été introduites : une dans le
`.gitlab-ci.yml`, deux dans le code. Elles ne se montrent pas en même temps.

## Objectif (état attendu)

1. GitLab **accepte** la configuration du pipeline. Son linter, dans
   **Build > Pipeline editor**, le confirme sur la branche choisie.
2. Les deux imports inutiles ont disparu du dépôt, dans `app/main.py` et
   `app/routes/health.py`.
3. Le **dernier** pipeline de la branche par défaut est **vert**.
4. Les journaux des jobs réussis portent la trace du contrôle de style **et**
   de la suite de tests.

## La méthode, qui est le vrai sujet

- un pipeline en échec **sans aucun job** est un refus de configuration, pas
  une erreur d'exécution. Le message est à lire sur le pipeline lui-même, ou
  dans l'éditeur de pipeline ;
- le journal d'un job en échec se lit **par la fin** : la dernière ligne donne
  le code de sortie, et les lignes au-dessus le résumé de l'outil ;
- une erreur de ruff tient en deux lignes : le code de règle avec son message,
  puis la position sous la forme `fichier:ligne:colonne`.

## Validation

```bash
dsoxlab check gl-02-lire-un-echec
```
