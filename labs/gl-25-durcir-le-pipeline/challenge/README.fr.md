# Challenge : durcir le runner

## Mission

Le projet `pipeline-craft` est dans la forge du lab, à l'adresse
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt vous attend
dans `/opt/dsoxlab/gl-25/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline rejoue deux attaques contre le runner, et les deux réussissent.

## Objectif (état attendu)

1. Le runner n'est **pas privilégié**.
2. `allowed_images` est définie, accepte l'image du pipeline légitime et refuse
   `alpine:3.20`.
3. `cap_drop` contient `ALL`, `security_opt` contient `no-new-privileges:true`.
4. Un pipeline a tourné sur `main` après le durcissement et `tester` a réussi.
5. Dans ce pipeline, les deux jobs d'attaque ont **échoué sur le refus**.

## À lire avant de commencer

`NOTE-RUNNER.txt`, à côté de la copie du dépôt dans `/opt/dsoxlab/gl-25`.

## Deux rappels

- la configuration du runner est un fichier qui appartient à root : utilisez `sudo` ;
- ne modifiez pas `.gitlab-ci.yml`. Une attaque bloquée est un job en échec : lisez son journal.

## Validation

```bash
dsoxlab check gl-25-durcir-le-pipeline
```
