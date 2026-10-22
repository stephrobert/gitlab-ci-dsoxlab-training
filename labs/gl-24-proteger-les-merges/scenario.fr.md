# Scénario

Le pipeline de `pipeline-craft` est **vert** : un job `tester`, puis un job
`deployer-production` qui déploie vers l'environnement `production`. Rien n'est
cassé. C'est précisément le problème : le projet ne porte **aucun verrou**.

Aujourd'hui, avec le rôle Developer, n'importe qui peut :

- pousser directement sur `main`, ou réécrire son historique ;
- créer un tag `v1.0.0`, ce que déploie un pipeline de release ;
- fusionner une merge request dont le pipeline est rouge, ou dont la remarque
  d'un relecteur est encore ouverte.

Un verrou n'est pas une ligne de `.gitlab-ci.yml`. C'est un **réglage que la
forge détient**, et la forge est la seule à le faire respecter. Le projet est
dans la forge du lab. Une copie du dépôt vous attend sur la machine, avec une
note : `NOTE-VERROUS.txt`.

## Mission

Quatre verrous, puis une preuve.

1. **Protéger `main`.** Un Developer ne doit plus pouvoir y pousser, le push
   forcé doit être interdit, et la fusion doit rester possible : une branche dans
   laquelle personne ne peut fusionner n'est pas protégée, elle est gelée.
2. **Protéger les tags de release.** Seuls les Maintainers créent un tag comme
   `v1.0.0`. Un tag se protège par un motif, qui doit couvrir vos tags de
   release.
3. **Exiger un pipeline vert avant toute fusion.**
4. **Exiger que toutes les discussions soient résolues avant toute fusion.**
5. **Prouver que les verrous laissent passer un déploiement légitime.** Lancez un
   pipeline sur `main` et attendez-le : `tester` et `deployer-production` doivent
   réussir tous les deux.

Le dernier temps n'est pas une formalité. Des verrous qui interdisent tout ne
protègent rien : ils protègent la production en la rendant impossible à déployer.

## Ce que le lab vérifie

1. `main` est protégée : personne en dessous de Maintainer n'y pousse, le push
   forcé est interdit, et quelqu'un peut y fusionner ;
2. un motif de tag protégé couvre `v1.0.0`, et seuls les Maintainers le créent ;
3. le projet exige un pipeline vert avant de fusionner ;
4. le projet exige des discussions résolues avant de fusionner ;
5. un pipeline a tourné sur `main` depuis le début, il est terminé, et les deux
   jobs `tester` et `deployer-production` ont réussi.

Le lab lit les **réglages** que la forge porte, par son API, et ce que le
pipeline a fait. Il ne lit jamais `.gitlab-ci.yml`, et il n'impose pas la façon
de poser les verrous : interface ou API.

## Deux limites à connaître

La forge ne date pas un verrou. Le lab ne peut pas prouver que votre pipeline a
tourné **après** la pose des verrous : il prouve qu'un pipeline a réussi depuis
le début. Lancez-le après, c'est tout l'intérêt de la preuve. Et le lab mesure le
**réglage**, pas le refus qu'il provoque : il n'essaie pas un push interdit.

## Ce qu'une licence ajoute

Tout ce qui précède fonctionne dans GitLab Community Edition. Deux autres
verrous viennent avec une licence Premium et ne sont pas pratiqués ici : la
**règle d'approbation** (une merge request doit être approuvée par des
personnes désignées) et l'**environnement protégé** (seuls des rôles désignés
déploient en `production`). Sur la forge du lab, l'API `protected_environments`
répond `404 Not Found`.
