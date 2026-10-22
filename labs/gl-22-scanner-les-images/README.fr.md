# Lab : scanner l'image, et cesser de livrer une faille critique

Un pipeline qui publie son image sans jamais la regarder, et une image qui porte
une vulnérabilité critique réelle. Vous scannez avec Trivy, gardez le rapport,
bloquez le pipeline sur une critique, et écartez le seul finding que l'équipe
sécurité a trié, en écrivant pourquoi.

Leçon compagnon :
[Scanners de sécurité](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/fondamentaux/securite-scanners/).

```bash
dsoxlab run gl-22-scanner-les-images
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-22/pipeline-craft (branche main).
dsoxlab challenge gl-22-scanner-les-images
dsoxlab check gl-22-scanner-les-images
```

La note se prend sur ce que la forge a vu : un job de scan qui a tourné, un
rapport Trivy conservé dans ses artefacts, un pipeline réellement échoué à cause
d'une critique, et une exception justifiée qui ne couvre que le finding trié.
Un `.gitlab-ci.yml` qui déclare un job de scan ne prouve rien.

## Ce que vous saurez faire

- scanner une image publiée avec Trivy depuis un pipeline GitLab CE ;
- conserver un rapport JSON même quand le job échoue ;
- faire échouer le pipeline sur une vulnérabilité critique, avant le déploiement ;
- écarter un faux positif dans `.trivyignore` en écrivant la raison à côté.

Ce lab exige l'accès à Docker Hub et à la base de vulnérabilités de Trivy depuis
la VM.
