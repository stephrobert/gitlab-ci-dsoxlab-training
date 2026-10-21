# Lab : faire dire au pipeline ce qu'il couvre

Des tests qui passent et ne disent rien de la part de code qu'ils traversent.
Imprimer la couverture, la faire pêcher par GitLab, et publier le rapport qui
montre les lignes manquantes.

Leçon compagnon :
[Rapports de qualité](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-10-rapports-qualite/).

```bash
dsoxlab run gl-10-rapports-de-qualite
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-10/pipeline-craft (branche main).
dsoxlab challenge gl-10-rapports-de-qualite
dsoxlab check gl-10-rapports-de-qualite
```

La note lit ce qui est arrivé à GitLab : le chiffre de couverture et le type
des artefacts publiés. Un pourcentage dit où l'on en est ; un rapport dit quoi
faire.
