# Challenge : décider quand le pipeline tourne

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-06/pipeline-craft` sur la VM, sur la branche `main`.

Tous ses jobs tournent à chaque push, sur n'importe quelle branche, et rien
n'est déployé.

## Objectif (état attendu)

1. Un job de déploiement a **réussi** automatiquement sur la branche par
   défaut.
2. Un autre job de déploiement attend une **décision humaine** (statut
   `manual`).
3. Le pipeline reste **vert**.
4. La configuration porte un bloc **`workflow:`**.

Le dépôt fournit `scripts/deploy-demo.sh <environnement>`, qui simule un
déploiement : inutile d'en écrire un.

## Ce qui n'est pas imposé

Ni le nom des jobs, ni celui du stage de déploiement, ni les conditions exactes
de vos règles, du moment que les quatre points ci-dessus sont vrais.

## Validation

```bash
dsoxlab check gl-06-controler-execution
```
