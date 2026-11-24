# Deux pannes muettes

## La situation

Un collègue a touché au `.gitlab-ci.yml` de `pipeline-craft` avant de partir en
congés. Depuis, l'équipe pousse et **rien ne se passe**.

Pas d'échec, pas d'avertissement, pas de job ignoré : l'onglet Pipelines reste
vide. Deux personnes ont déjà relancé leur push, pensant à un problème de
réseau.

Et ce n'est que la première panne. La seconde attend derrière, et elle est de
la même famille : elle ne dit rien non plus.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Faites repartir le pipeline, en diagnostiquant deux pannes qui ne produisent
**aucun message**.

Ce sont les plus coûteuses, parce qu'il n'y a rien à lire. Les reconnaître
demande de savoir **ce qui devrait être là** :

- **un onglet Pipelines vide** n'est pas une erreur, c'est une absence. Rien
  n'a échoué, rien n'a été ignoré : rien n'a été créé. La question à se poser
  est « qu'est-ce qui décide qu'un pipeline naisse ? ». Le linter de GitLab
  répond à celle-là : interrogé avec `dry_run`, il **évalue les règles** et
  rend `valid: false` avec « The pipeline did not run. Review the
  workflow:rules configuration » quand aucun pipeline ne naîtrait ;
- **un job qui reste en attente** n'échoue jamais. Il attend un runner capable
  de le prendre, et si aucun ne l'est, il attend indéfiniment. La question
  devient « ce job demande-t-il quelque chose que personne ne peut fournir ? ».

## Ce que le lab vérifie

1. un **pipeline existe** sur la branche par défaut ;
2. **aucun job n'est resté en attente**, le linter a réellement tourné, et
   aucun job n'a échoué.

Le second point porte plusieurs exigences, et ce n'est pas un raccourci : sur
un état sans pipeline, « aucun job n'a échoué » est vrai, donc cela ne peut pas
faire un test à soi seul.

## Un statut à ne pas confondre avec une panne

Un job **`manual`** attend une décision humaine : c'est un job sain, et le
pipeline en porte un depuis un lab précédent. Ce n'est pas lui qui est bloqué.

## Où regarder

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft

# Le linter EVALUE les regles : il dit si un pipeline naitrait, et pourquoi
# non. C'est le diagnostic le plus direct de la premiere panne.
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/ci/lint?dry_run=true&ref=main" \
  | jq '{valid, errors}'

# Y a-t-il un pipeline, et depuis quelle source ?
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=5" \
  | jq -r '.[] | "\(.id) \(.source) \(.status)"'

# Quels tags le runner de l'instance porte-t-il ?
curl -s -H "PRIVATE-TOKEN: $JETON" "http://gitlab-1.lab/api/v4/runners/all" \
  | jq -r '.[] | {description, tag_list}'
```

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-11/pipeline-craft` sur la VM, sur la branche `main`.

Vous poussez, et aucun pipeline n'apparaît. Derrière cette panne, une seconde
attend.

### Objectif (état attendu)

1. Un **pipeline existe** sur la branche par défaut.
2. **Aucun job n'est resté en attente**, le linter a tourné, aucun job n'a
   échoué.

### Deux rappels

- un job **`manual`** attend une décision humaine : il est sain, ce n'est pas
  lui qui bloque ;
- retirer un job du pipeline le fait disparaître des jobs bloqués sans rien
  réparer. Le lab vérifie que le linter a **réellement tourné**.

### Validation

```bash
dsoxlab check gl-11-diagnostiquer-un-job-bloque
```
