# Un orchestrateur, et un fichier par étape

## La situation

Le pipeline de `pipeline-craft` est propre. Plus de duplication, un cache qui
sert, des jobs qui ne s'attendent plus : le lab précédent a fait son travail.

Il fait quatre-vingts lignes. Six jobs, quatre étapes, un workflow, des
variables, deux gabarits. Tout y est juste, et plus personne ne le lit en
entier : pour changer la version de Python, il faut parcourir le fichier
jusqu'au bon bloc en espérant ne pas en oublier un.

Et une nouvelle équipe arrive, qui voudrait ajouter deux jobs de sécurité. Dans
ce fichier.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Découpez le pipeline, et gardez un orchestrateur lisible.

La question à trancher n'est pas « où couper » mais **ce qui reste au
centre** :

- **ce qui est commun** reste dans `.gitlab-ci.yml` : la liste des étapes, qui
  dit l'ordre, et le `workflow:`, qui dit quand un pipeline naît. Dispersés
  dans quatre fichiers, il faudrait ouvrir les quatre pour répondre à ces deux
  questions ;
- **ce qui est propre à une étape** part avec elle, dans un fichier inclus.

## Une surprise utile

Les fichiers inclus **ne cloisonnent rien** : GitLab les fusionne tous avant
d'évaluer quoi que ce soit. Un job caché déclaré dans un fichier est donc
visible depuis un autre, et un job peut l'étendre sans rien importer.

Une **ancre YAML**, elle, ne traverse pas les fichiers : elle est résolue
fichier par fichier, avant la fusion. C'est la différence la plus utile à
retenir entre les deux mécaniques du lab précédent.

## Ce que le lab vérifie

Un seul test, parce qu'une seule chose change vraiment :

1. **GitLab rapporte plusieurs fichiers inclus**. Il les nomme lui-même : une
   inclusion n'est pas résolue dans le YAML, elle est faite par lui ;
2. le comportement **n'a pas bougé** : les jobs tournent, aucun n'échoue, la
   couverture remonte ;
3. l'orchestrateur **garde** les étapes et le workflow.

Les points 2 et 3 sont des garde-fous, vrais dès l'état de départ : ils
s'ajoutent au premier au lieu de faire des tests à eux seuls.

## Une différence avec le lab précédent

Au lab 13, la note devait lire votre fichier : `extends` et les ancres sont
résolus avant que GitLab ne les voie. Ici, GitLab **sait** qu'il a inclus des
fichiers, et son linter le dit. La mesure revient donc du côté du serveur, là
où elle doit être.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-14/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline fait quatre-vingts lignes, et tout y est juste.

### Objectif (état attendu)

1. GitLab rapporte **au moins deux fichiers inclus**.
2. Le comportement n'a pas bougé : aucun job en échec, au moins quatre jobs
   réussis, et la couverture remonte toujours.
3. La configuration fusionnée porte encore `stages:` et `workflow:`.

### Deux choses à savoir

- les fichiers inclus **ne cloisonnent pas** : un job caché déclaré dans l'un
  est visible depuis l'autre, GitLab fusionnant tout avant d'évaluer ;
- une **ancre YAML** ne traverse pas les fichiers. Elle doit vivre dans le même
  fichier que son `<<:`.

### Vérifier ce que GitLab a inclus

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/ci/lint?dry_run=true&ref=main" \
  | jq '{valid, includes}'
```

Un `include:` mal écrit ne provoque pas toujours une erreur : il peut
simplement n'inclure personne.

### Validation

```bash
dsoxlab check gl-14-externaliser-les-jobs
```
