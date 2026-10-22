# Challenge : fiabiliser sans masquer les échecs

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-18/pipeline-craft` sur la VM, sur la branche `main`.

Le pipeline est « failed » sans un seul job. Réparez-le, puis fiabilisez-le.

## Objectif (état attendu)

1. GitLab **accepte** la configuration de `main`, et un pipeline y tourne avec
   ses jobs.
2. Chaque job de déploiement porte un **verrou**, et la forge porte réellement
   ces verrous.
3. Une **relance** existe, et **aucune** ne couvre un échec de script.
4. Les déploiements portent un **délai** et ne sont **plus annulables**.

## Les deux temps

1. trouver pourquoi GitLab refuse la configuration, et corriger ;
2. poser relance, délais, verrous et interdiction d'annuler.

## Quand le pipeline ne dit rien, demander au linter

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/ci/lint?dry_run=true&ref=main" \
  | jq -r '.valid, .errors[]?'
```

Le même appel sert à la fin : quand il répond `true`, il rend aussi la
configuration **compilée**, celle que le lab note.

## Voir les verrous que la forge a créés

```bash
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/resource_groups" \
  | jq -r '.[] | "\(.key) \(.process_mode)"'
```

La liste est vide au départ. Un verrou n'existe qu'à partir du moment où un
pipeline qui le porte a été créé : poussez votre configuration avant de
compter.

## Deux rappels

- une relance qui couvre un échec de script transforme un test instable en test
  qui finit par passer **au hasard**. Les raisons se nomment une par une ;
- le fichier principal autorise **tous** les jobs à être annulés. Pour un
  déploiement, c'est à défaire job par job.

## Validation

```bash
dsoxlab check gl-18-fiabiliser-sans-masquer
```
