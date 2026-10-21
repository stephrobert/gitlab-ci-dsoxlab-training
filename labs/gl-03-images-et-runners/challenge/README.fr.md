# Challenge : la bonne image pour chaque job

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-03/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline a trois jobs, tous sur `python:3.12`, et celui qui construit
l'image Docker échoue.

## Objectif (état attendu)

1. Le **dernier** pipeline de la branche par défaut est **vert**.
2. Un job réussi porte un `docker build` **mené à bien**.
3. Un **service Docker** a été démarré pour ce job.
4. Plus aucun job ne tire l'image complète `python:3.12`.

## Ce qui n'est pas imposé

Ni le nom des jobs, ni l'image de remplacement des jobs Python : une variante
`-slim`, `-alpine` ou toute autre base légère convient. Le point 4 mesure que
le choix a été fait, pas lequel.

## Validation

```bash
dsoxlab check gl-03-images-et-runners
```
