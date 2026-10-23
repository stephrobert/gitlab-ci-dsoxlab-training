# Épreuve de niveau : un pipeline qu'on peut auditer

Fin du niveau 4. Un pipeline vert qui déploie en production, et dont personne
ne pourrait se porter garant devant un auditeur.

Plan du niveau :
[labs GitLab CI/CD](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/).

```bash
dsoxlab run gl-ep3-un-pipeline-qu-on-peut-auditer
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt vous attend dans /opt/dsoxlab/gl-ep3/pipeline-craft (branche main).
dsoxlab challenge gl-ep3-un-pipeline-qu-on-peut-auditer
dsoxlab check gl-ep3-un-pipeline-qu-on-peut-auditer
```

Épreuve sans indice : les défauts ne sont pas nommés, et la note se prend sur
les réglages et l'état du pipeline que la forge rapporte par son API. Aucune
fonctionnalité Premium n'est nécessaire.
