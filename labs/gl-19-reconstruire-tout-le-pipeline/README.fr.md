# Lab : reconstruire tout le pipeline

L'épreuve de synthèse du parcours. Le dépôt n'a plus aucun fichier de CI : un
cahier des charges, et tout à reconstruire.

Leçon compagnon :
[Capstone industriel](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-19-capstone-industriel/).

```bash
dsoxlab run gl-19-reconstruire-tout-le-pipeline
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-19/pipeline-craft (branche main).
# Le cahier des charges est dans CAPSTONE-LAB-19.md, à la racine du dépôt.
# La contrainte de registre de cet environnement est rappelée dans
# /opt/dsoxlab/gl-19/REGISTRE-DU-LAB.txt.
dsoxlab challenge gl-19-reconstruire-tout-le-pipeline
dsoxlab check gl-19-reconstruire-tout-le-pipeline
```

La note se prend sur l'état que la forge montre : cinq étapes qui portent des
jobs, les fichiers que GitLab a réellement inclus, les instances de la matrice,
les cas de test remontés, le pipeline enfant déclenché, les étiquettes du
registre et les verrous de déploiement. Aucun nom de job n'est imposé.
