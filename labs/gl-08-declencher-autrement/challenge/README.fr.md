# Challenge : déclencher un pipeline sans pousser

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-08/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline ne sait naître que d'un push, et le projet n'a ni planification ni
jeton de déclenchement.

## Objectif (état attendu)

1. Une **planification** existe et est **active**.
2. Un **jeton de déclenchement** existe.
3. Un pipeline a tourné depuis une source **autre qu'un push**, sans job en
   échec.
4. Un job apparaît **seulement** dans ce pipeline, pas dans celui d'un push.

## Deux pistes

Déclencher par le jeton, depuis la VM :

```bash
curl -X POST --form token=VOTRE_JETON --form ref=main \
  http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/trigger/pipeline
```

La planification se crée dans l'interface (`Build > Pipeline schedules`) ou par
l'API. Son heure n'a pas d'importance pour la note : ce qui compte est qu'elle
existe et soit active.

Pour la jouer tout de suite, sans attendre son heure :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -X POST -H "PRIVATE-TOKEN: $JETON" \
  http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/pipeline_schedules/1/play
```

Le pipeline qui en naît porte la source `schedule`, celle dont un job peut
dépendre.

## Validation

```bash
dsoxlab check gl-08-declencher-autrement
```
