# Challenge : votre premier pipeline

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-01/pipeline-craft` sur la VM. Il n'a **aucun
`.gitlab-ci.yml`** et son onglet Pipelines est vide.

Le dépôt porte déjà tout ce qu'il faut pour travailler : le code dans `app/`,
une suite de tests dans `tests/`, les dépendances de développement dans
`requirements-dev.txt` (ruff et pytest compris), et un `Dockerfile`. Les trois
commandes passent à la main : `ruff check app/ tests/`, `pytest -v` et
`docker build -t pipeline-craft:test .`.

## Objectif (état attendu)

1. Le dépôt porte un `.gitlab-ci.yml` sur sa branche par défaut.
2. Le **dernier** pipeline de cette branche est **vert**.
3. Ce pipeline compte **au moins trois jobs réussis**, répartis sur **plus
   d'une étape** : un pipeline d'un seul job ne montre pas ses étapes.
4. Les journaux de ces jobs portent la trace des **trois gestes** : contrôle du
   style, suite de tests, construction de l'image.

Le nom des jobs, celui des étapes et le contenu de votre fichier ne comptent
pas : la note lit l'état du pipeline dans l'API de GitLab, pas vos
intentions.

## Validation

```bash
dsoxlab check gl-01-premier-pipeline
```
