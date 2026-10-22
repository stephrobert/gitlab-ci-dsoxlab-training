# Lab : une matrice de tests

Des tests qui ne connaissent qu'une version de Python, et une production qui en
fait tourner deux. Construire une matrice, lui faire varier quelque chose de
réel, et lier la construction à toutes ses combinaisons.

Leçon compagnon :
[Matrices](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-15-matrices/).

```bash
dsoxlab run gl-15-une-matrice-de-tests
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-15/pipeline-craft (branche main).
dsoxlab challenge gl-15-une-matrice-de-tests
dsoxlab check gl-15-une-matrice-de-tests
```

La note lit les jobs que GitLab a instanciés et les images qu'ils ont tirées :
une matrice qui ne fait rien varier relance le même travail plusieurs fois, et
ce lab-là refuse de la valider.
