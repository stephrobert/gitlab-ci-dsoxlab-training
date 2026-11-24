# Décider quand le pipeline tourne

## La situation

Le pipeline de `pipeline-craft` fonctionne, et il fonctionne **trop**. Chaque
push déclenche tout : sur une branche de brouillon, sur une branche qu'on vient
de créer pour sauvegarder un essai, sur une correction de faute de frappe dans
le README. Trois jobs, chaque fois, avec leurs installations de paquets et leur
construction d'image.

Et à l'autre bout, rien n'est déployé. Le pipeline construit une image, et
s'arrête là. Mettre le code en recette se fait à la main, quand quelqu'un y
pense.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Reprenez la main sur le **quand**.

Trois niveaux de décision, du plus large au plus fin, et les confondre est
l'erreur la plus courante :

- **le pipeline naît-il ?** C'est la question du bloc `workflow:`. Sans lui, un
  pipeline part à chaque push, sur chaque branche ;
- **ce job entre-t-il dans le pipeline qui est né ?** C'est la question des
  `rules:` posées sur le job ;
- **ce job part-il tout seul ?** Un job peut entrer dans le pipeline et
  attendre qu'un humain le déclenche.

Ajoutez par ailleurs deux déploiements : la **recette**, qui part toute seule
quand la branche par défaut bouge, et la **production**, qui attend une
décision.

## Ce que le lab vérifie

1. un job de déploiement a **réussi** automatiquement sur la branche par
   défaut ;
2. un autre job de déploiement attend une **décision humaine**, en statut
   `manual` ;
3. **aucun job n'a échoué** : ajouter deux jobs ne casse pas ce qui
   marchait. Attention au statut du pipeline, qui passe à **`manual`** et non
   à « success » tant que le déploiement de production attend sa décision :
   c'est l'état voulu, pas un échec ;
4. la configuration porte un bloc `workflow:`.

Une précision sur le point 4, parce qu'elle est honnête : l'effet d'un
`workflow:` ne s'observe qu'en poussant sur une branche qui ne doit rien
déclencher, ce qu'un test n'a pas à faire. Le lab lit donc la configuration
**que GitLab a comprise**, celle que son linter rend, et pas votre fichier.

## Une particularité de la forge du lab

Le registre de ce GitLab est en **HTTP**. Le service Docker du job de
construction en est informé par une option, posée pour vous dans l'état de
départ. Sur gitlab.com, en HTTPS, la question ne se pose pas.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-06/pipeline-craft` sur la VM, sur la branche `main`.

Tous ses jobs tournent à chaque push, sur n'importe quelle branche, et rien
n'est déployé.

### Objectif (état attendu)

1. Un job de déploiement a **réussi** automatiquement sur la branche par
   défaut.
2. Un autre job de déploiement attend une **décision humaine** (statut
   `manual`).
3. **Aucun job n'a échoué.** Le statut du pipeline lui-même sera
   **`manual`** tant que le déploiement de production attend : c'est l'état
   voulu.
4. La configuration porte un bloc **`workflow:`**.

Le dépôt fournit `scripts/deploy-demo.sh <environnement>`, qui simule un
déploiement : inutile d'en écrire un.

### Ce qui n'est pas imposé

Ni le nom des jobs, ni celui du stage de déploiement, ni les conditions exactes
de vos règles, du moment que les quatre points ci-dessus sont vrais.

### Validation

```bash
dsoxlab check gl-06-controler-execution
```
