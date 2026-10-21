# Lab : faire sortir le secret du dépôt

Un mot de passe en clair à deux endroits, et un job qui l'affiche. Le retirer,
le déclarer masqué et protégé dans la forge, et prouver qu'il ne fuit plus.

Leçon compagnon :
[Sortir les secrets](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-05-sortir-les-secrets/).

```bash
dsoxlab run gl-05-sortir-les-secrets
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-05/pipeline-craft (branche main).
dsoxlab challenge gl-05-sortir-les-secrets
dsoxlab check gl-05-sortir-les-secrets
```

La note lit le dépôt, les variables CI/CD du projet et les journaux des jobs.
Les tests ne lisent jamais la **valeur** d'une variable : un message d'échec
qui la contiendrait publierait le secret.
