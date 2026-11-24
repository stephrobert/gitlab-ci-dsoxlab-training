# Votre premier pipeline

## La situation

On vient de vous confier `pipeline-craft`, un petit service FastAPI sur lequel
trois personnes poussent chaque jour. Il a des tests dans `tests/`, un linter
configuré dans `pyproject.toml` et un `Dockerfile`, et tout fonctionne :
`ruff check app/ tests/`, `pytest -v` et `docker build .` passent sur votre
machine.

Rien ne les lance sur le serveur. Le projet **n'a aucun `.gitlab-ci.yml`** :
GitLab n'a donc jamais rien construit, jamais lancé un test, et l'onglet
Pipelines est vide. Le mois dernier, deux fois, une modification qui cassait la
suite de tests a atteint la branche par défaut, et personne ne l'a vu avant
qu'un collègue ne récupère le code.

Une instance GitLab vous attend sur `gitlab-1.lab`, avec un runner déjà
enregistré et capable de prendre les jobs sans tag. Le dépôt y est, sur sa
branche `main`.

## Mission

Faites faire au serveur ce que votre machine fait déjà, et prouvez-le.

À la fin, le dernier pipeline du projet sur la branche par défaut doit être
**vert**, et il doit avoir réellement fait trois choses : contrôlé le style du
code, joué la suite de tests, et construit l'image. Pas un pipeline qui existe,
et pas un pipeline vert parce qu'il ne fait rien.

L'organisation est la vôtre. Le lab ne regarde pas quelles commandes vous
mettez dans quel job, ni comment vous nommez les choses. Il regarde trois
choses, lues dans l'API de GitLab : que le dernier pipeline de la branche par
défaut est vert, qu'il compte au moins trois jobs réussis répartis sur
plusieurs étapes, et que les journaux de ces jobs portent la trace des trois
gestes attendus.

Vous saurez que c'est fini quand l'onglet Pipelines affichera une exécution
verte dont les jobs couvrent les trois étapes.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-01/pipeline-craft` sur la VM. Il n'a **aucun
`.gitlab-ci.yml`** et son onglet Pipelines est vide.

Le dépôt porte déjà tout ce qu'il faut pour travailler : le code dans `app/`,
une suite de tests dans `tests/`, les dépendances de développement dans
`requirements-dev.txt` (ruff et pytest compris), et un `Dockerfile`. Les trois
commandes passent à la main : `ruff check app/ tests/`, `pytest -v` et
`docker build -t pipeline-craft:test .`.

### Objectif (état attendu)

1. Le dépôt porte un `.gitlab-ci.yml` sur sa branche par défaut.
2. Le **dernier** pipeline de cette branche est **vert**.
3. Ce pipeline compte **au moins trois jobs réussis**, répartis sur **plus
   d'une étape** : un pipeline d'un seul job ne montre pas ses étapes.
4. Les journaux de ces jobs portent la trace des **trois gestes** : contrôle du
   style, suite de tests, construction de l'image.

Le nom des jobs, celui des étapes et le contenu de votre fichier ne comptent
pas : la note lit l'état du pipeline dans l'API de GitLab, pas vos
intentions.

### Validation

```bash
dsoxlab check gl-01-premier-pipeline
```
