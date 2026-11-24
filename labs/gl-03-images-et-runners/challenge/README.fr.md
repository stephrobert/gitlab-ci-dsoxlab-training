# La bonne image pour chaque job

## La situation

Le pipeline de `pipeline-craft` tourne, mais il tourne mal. Les trois jobs
partagent la même image, `python:3.12`, l'image Python complète : près d'un
gigaoctet téléchargé pour chaque job, alors que lancer ruff n'en demande
qu'une fraction.

Surtout, le job qui construit l'image Docker **échoue systématiquement**.
Personne dans l'équipe ne voit pourquoi : la commande est la bonne, et elle
passe sur les postes de développement.

Le projet est dans la forge du lab, avec son pipeline en échec. Une copie du
dépôt vous attend sur la machine.

## Mission

Donnez à chaque job l'image qui correspond à son travail, et faites aboutir la
construction de l'image.

Deux idées à tenir ensemble :

- **un job tourne dans l'image qu'on lui donne**, et ne dispose que de ce que
  cette image contient. Une image Python exécute Python, pas Docker ;
- **construire une image demande un démon**, en plus du client. Dans un
  pipeline, ce démon ne vient pas de la machine du runner : il se déclare.

Pour les jobs Python, l'image complète fait le travail, mais une variante
allégée le fait aussi, pour une fraction du téléchargement.

## Ce que le lab vérifie

La note se lit dans les **journaux des jobs**, où GitLab Runner inscrit l'image
qu'il a tirée :

1. le dernier pipeline de la branche par défaut est **vert** ;
2. un job réussi porte un `docker build` **mené à bien** ;
3. un **service Docker** a bien été démarré pour ce job ;
4. plus aucun job ne tire l'image complète `python:3.12`.

Le point 4 ne dicte pas l'image de remplacement : `-slim`, `-alpine` ou une
autre base légère conviennent. Ce qui est mesuré, c'est que le choix a été
fait.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-03/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline a trois jobs, tous sur `python:3.12`, et celui qui construit
l'image Docker échoue.

### Objectif (état attendu)

1. Le **dernier** pipeline de la branche par défaut est **vert**.
2. Un job réussi porte un `docker build` **mené à bien**.
3. Un **service Docker** a été démarré pour ce job.
4. Plus aucun job ne tire l'image complète `python:3.12`.

### Ce qui n'est pas imposé

Ni le nom des jobs, ni l'image de remplacement des jobs Python : une variante
`-slim`, `-alpine` ou toute autre base légère convient. Le point 4 mesure que
le choix a été fait, pas lequel.

### Validation

```bash
dsoxlab check gl-03-images-et-runners
```
