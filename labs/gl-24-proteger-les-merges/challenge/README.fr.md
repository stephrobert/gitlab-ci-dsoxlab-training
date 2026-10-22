# Challenge : verrouiller la branche, les tags et la fusion

## Mission

Le projet `pipeline-craft` est dans la forge du lab, à l'adresse
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt vous attend
dans `/opt/dsoxlab/gl-24/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline est vert et déploie en `production`. Le projet ne porte aucun
verrou.

## Objectif (état attendu)

1. `main` est **protégée** : les Developers ne peuvent pas y pousser, le push
   forcé est interdit, et quelqu'un peut y fusionner.
2. Un motif de **tag protégé** couvre `v1.0.0` ; seuls les Maintainers le créent.
3. La fusion **exige un pipeline vert**.
4. La fusion **exige des discussions résolues**.
5. Un pipeline a tourné sur `main` depuis le début et ses deux jobs, `tester` et
   `deployer-production`, ont réussi.

## À lire avant de commencer

`NOTE-VERROUS.txt`, à côté de la copie du dépôt dans `/opt/dsoxlab/gl-24`.

## Deux rappels

- un verrou est un réglage de la forge : rien dans `.gitlab-ci.yml` ne le crée ;
- lancez le pipeline de preuve **après** la pose des verrous : la forge ne les
  date pas, le lab ne voit pas l'ordre, vous si.

## Validation

```bash
dsoxlab check gl-24-proteger-les-merges
```
