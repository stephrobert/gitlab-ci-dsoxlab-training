# Épreuve de niveau : un pipeline à industrialiser

Fin du niveau 3. Un pipeline vert qui n'a été industrialisé qu'à moitié : il
tourne, et personne ne voudrait ni le maintenir ni lui faire confiance sous
charge.

Cette épreuve n'est pas `gl-19-reconstruire-tout-le-pipeline`. Ce lab-là
construit un pipeline depuis un cahier des charges, avec des indices. Ici un
pipeline existe déjà, et c'est à vous de diagnostiquer ce qui cloche.

Plan du niveau :
[labs GitLab CI/CD](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/).

```bash
dsoxlab run gl-ep4-un-pipeline-a-industrialiser
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt vous attend dans /opt/dsoxlab/gl-ep4/pipeline-craft (branche main).
dsoxlab challenge gl-ep4-un-pipeline-a-industrialiser
dsoxlab check gl-ep4-un-pipeline-a-industrialiser
```

Épreuve sans indice : les défauts ne sont pas nommés, et la note se prend sur
la configuration et l'état du pipeline que la forge rapporte par son API.
Aucune fonctionnalité Premium n'est nécessaire. Comptez environ 70 minutes.
