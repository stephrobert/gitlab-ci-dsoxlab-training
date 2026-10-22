# Lab : fiabiliser sans masquer les échecs

Un pipeline « failed » sans un seul job, et une fois réparé, aucune défense :
pas de délai, pas de relance, et deux déploiements qui peuvent partir ensemble
sur le même environnement.

Leçon compagnon :
[Fiabilité](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-18-fiabilite/).

```bash
dsoxlab run gl-18-fiabiliser-sans-masquer
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-18/pipeline-craft (branche main).
dsoxlab challenge gl-18-fiabiliser-sans-masquer
dsoxlab check gl-18-fiabiliser-sans-masquer
```

La note se prend sur les verrous de déploiement que la forge a réellement
créés, et sur la configuration telle que GitLab l'a compilée : une relance qui
rattrape un échec de script fait échouer le lab, parce qu'elle masque ce
qu'elle devrait signaler.
