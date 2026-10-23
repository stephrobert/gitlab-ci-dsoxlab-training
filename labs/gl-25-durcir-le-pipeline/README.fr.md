# Lab : durcir le runner, et fermer ce qui était grand ouvert

Un pipeline tourne sur un runner grand ouvert, et il rejoue deux attaques contre
lui : les deux réussissent. Vous durcissez la configuration du runner, vous
relancez le pipeline, et vous prouvez que les deux attaques sont maintenant
bloquées alors que le job légitime passe encore.

Leçon associée :
[GitLab CI : durcir vos pipelines en 10 mesures](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/securite/durcissement/).

```bash
dsoxlab run gl-25-durcir-le-pipeline
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt vous attend dans /opt/dsoxlab/gl-25/pipeline-craft (branche main).
dsoxlab challenge gl-25-durcir-le-pipeline
dsoxlab check gl-25-durcir-le-pipeline
```

La note porte sur la configuration du runner (`/etc/gitlab-runner/config.toml`) et
sur les journaux des jobs que le pipeline a exécutés. Rien dans `.gitlab-ci.yml`
ne durcit un runner.

## Ce que vous saurez faire

- dire ce que `privileged = true` donne à un job, et le désactiver ;
- restreindre les images qu'un runner accepte, en sachant qu'une clé absente autorise tout ;
- retirer les capacités Linux dont un conteneur n'a pas besoin ;
- prouver un durcissement en rejouant l'attaque et en lisant le refus dans le journal du job.

## Avant de commencer

- les bases de `gitlab-ci` : un job, un stage, un runner. Vous savez lire un fichier TOML ;
- vous modifiez un fichier appartenant à root avec `sudo` ;
- aucun service payant ni édition Premium ou Ultimate n'est nécessaire.

`dsoxlab clean` remet le runner dans son état de départ (privilégié, sans liste
d'images), pour que le lab suivant trouve le runner qu'il attend.

Un runner durci ne sait plus faire du Docker-in-Docker, qui exige `privileged = true`.
La page de la leçon explique les options (un runner dédié aux builds, ou un
constructeur sans démon) ; ce lab ne les pratique pas.
