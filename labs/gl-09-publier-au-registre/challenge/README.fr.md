# Publier l'image, et la garder traçable

## La situation

Le pipeline de `pipeline-craft` construit une image Docker à chaque passage sur
la branche par défaut. Puis le job se termine, et l'image disparaît avec lui.

Personne ne peut la déployer : il faudrait la reconstruire, en espérant obtenir
la même. Et quand la recette tombe en panne, personne ne peut dire quelle
version tourne, parce qu'aucune image n'a de nom durable.

La forge du lab a un **registre de conteneurs**, et il est vide.

Le projet est dans la forge. Une copie du dépôt vous attend sur la machine.

## Mission

Publiez l'image depuis le pipeline, sous un nom qui désigne le code qu'elle
contient.

Deux idées, et la seconde est celle qui compte :

- **publier**, c'est s'authentifier puis pousser. GitLab fournit au job tout ce
  qu'il faut : l'adresse du registre, un identifiant et un mot de passe
  jetables, et le chemin complet de l'image du projet. Trois variables
  `CI_REGISTRY_*` à connaître ;
- **rester traçable**, c'est nommer l'image d'après le **commit**. Un tag qui
  désigne un commit précis permet de dire, six mois plus tard, quel code tourne
  en production. Un tag mobile ne le permet pas.

## Une particularité de la forge du lab

Le registre de ce GitLab écoute en **HTTP**. Le service Docker du job en est
informé par une option, posée pour vous dans l'état de départ. Sur gitlab.com,
en HTTPS, la question ne se pose pas.

## Ce que le lab vérifie

1. le registre du projet porte **au moins une image** ;
2. un tag publié porte le **SHA court du dernier commit** de la branche par
   défaut ;
3. le journal d'un job réussi montre que c'est **le pipeline** qui a publié,
   pas une main sur un clavier ;
4. aucun job du pipeline n'a échoué.

Le point 2 est le cœur du lab. Un préfixe ou un suffixe autour du SHA ne gêne
pas : `sha-1a2b3c4d` convient autant que `1a2b3c4d`. Ce qui est refusé, c'est
qu'aucun tag ne désigne le commit.

## Sur le tag `latest`

Vous pouvez en publier un, le lab l'accepte. Il ne l'exige pas, et ce n'est pas
un oubli : un tag mobile invite celui qui consomme l'image à prendre une
référence qui bouge sous ses pieds. Le tag du commit, lui, dit toujours la même
chose.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-09/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline construit une image et la jette. Le registre du projet est vide.

### Objectif (état attendu)

1. Le registre du projet porte **au moins une image**.
2. Un tag publié porte le **SHA court du dernier commit**.
3. Le journal d'un job réussi montre l'envoi.
4. Aucun job n'a échoué.

### Les variables que GitLab fournit

| Variable | Ce qu'elle contient |
|---|---|
| `$CI_REGISTRY` | l'adresse du registre de l'instance |
| `$CI_REGISTRY_IMAGE` | le chemin complet de l'image de ce projet |
| `$CI_REGISTRY_USER` et `$CI_REGISTRY_PASSWORD` | des identifiants jetables, valables le temps du job |
| `$CI_COMMIT_SHORT_SHA` | le SHA court du commit qui a déclenché le pipeline |

Vérifier le résultat, depuis la VM :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/registry/repositories?tags=true" \
  | jq '.[] | {path, tags: [.tags[].name]}'
```

L'interface montre la même chose sous **Deploy > Container Registry**.

### Validation

```bash
dsoxlab check gl-09-publier-au-registre
```
