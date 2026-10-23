# Lab : protéger ce qui fusionne, et ce qui déploie

Un pipeline vert déploie en production depuis un projet qui ne porte aucun
verrou. Vous protégez la branche `main`, les tags de release, vous exigez un pipeline vert et des discussions résolues avant
toute fusion, et vous prouvez que les verrous laissent passer un déploiement
légitime.

Leçon associée :
[GitLab CI : branches et tags protégés](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/securite/branches-protegees/).

```bash
dsoxlab run gl-24-proteger-les-merges
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt vous attend dans /opt/dsoxlab/gl-24/pipeline-craft (branche main).
dsoxlab challenge gl-24-proteger-les-merges
dsoxlab check gl-24-proteger-les-merges
```

La note porte sur les réglages que la forge détient, lus dans son API : une
branche protégée, un motif de tag protégé, et deux
conditions de fusion. Un `.gitlab-ci.yml` n'en prouve aucun.

## Ce que vous saurez faire

- protéger une branche, et dire qui peut pousser et qui peut fusionner ;
- protéger des tags de release ;
- exiger un pipeline vert et des discussions résolues avant une fusion ;
- vérifier qu'un verrou protège sans bloquer le déploiement légitime.

Ce lab n'exige aucun service payant ni édition Premium ou Ultimate de GitLab. La
règle d'approbation et l'environnement protégé, qui demandent une licence, est nommée dans le scénario et
n'est pas pratiquée.
