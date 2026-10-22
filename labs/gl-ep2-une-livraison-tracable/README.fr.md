# Épreuve de niveau : une livraison qu'on peut retracer

Fin du niveau 2. Une chaîne qui construit, teste et déploie sans laisser la
moindre trace de ce qu'elle a livré, et un pipeline qui ne finit jamais.

Plan du niveau :
[Labs GitLab CI/CD](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/).

```bash
dsoxlab run gl-ep2-une-livraison-tracable
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-ep2/pipeline-craft (branche main).
dsoxlab challenge gl-ep2-une-livraison-tracable
dsoxlab check gl-ep2-une-livraison-tracable
```

Épreuve sans indice : les quatre défauts ne sont pas nommés, et la note se
prend sur ce que la forge porte, environnements, déploiements enregistrés,
étiquettes du registre et état des jobs.
