# Scénario

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
