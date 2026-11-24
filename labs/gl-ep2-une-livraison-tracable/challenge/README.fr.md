# Épreuve : une livraison qu'on peut retracer

## La situation

C'est l'épreuve de fin du niveau 2, celui qui s'appelle « Livrer ». Il n'y a
pas de pas à pas, pas d'indice, et les défauts ne sont pas nommés.

La chaîne de ce projet construit, teste et déploie. Elle ne laisse aucune
trace.

Personne ne peut répondre à ces questions, et pourtant elles se posent chaque
semaine :

- **qu'est-ce qui tourne en production, et depuis quand ?**
- **sur quelle image ce déploiement reposait-il ?**
- **qui a décidé de livrer ?**

Et un quatrième problème empêche de répondre aux trois premières : le pipeline
ne finit jamais.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Rendre la livraison **traçable** : quatre traces manquent, à vous de les
trouver et de les faire exister.

C'est la compétence du niveau, et elle est mal comprise. Livrer, ce n'est pas
copier des fichiers sur un serveur : c'est pouvoir dire, six mois plus tard,
quelle version tourne où, d'où elle vient, et qui l'a décidée. Un déploiement
qu'on ne peut pas retracer n'a pas eu lieu, du point de vue de l'équipe qui
devra le reprendre.

## Un défaut bloque les autres, commencez par là

Un job peut ne pas démarrer **sans pour autant échouer**. Il n'y a alors aucun
message, aucun journal, et le pipeline reste en cours indéfiniment : tout ce
qui vient après n'arrive jamais.

C'est la panne la plus désagréable de GitLab CI, parce qu'elle ne produit rien
à lire. Vous l'avez diagnostiquée dans un lab de ce niveau : le réflexe est de
comparer ce que le job **demande** avec ce que les runners du projet
**offrent**.

## Ce que l'épreuve note

Elle note **l'état laissé dans la forge**, jamais les commandes tapées :

1. aucun job du dernier pipeline n'est en attente, et aucun n'a échoué ;
2. le projet porte au moins un **environnement**, et au moins un
   **déploiement réussi** y est enregistré ;
3. le **registre** du projet porte au moins une étiquette ;
4. aucun job de production n'est parti de lui-même sur la branche par défaut.

## Ce que l'épreuve ne note pas

Ni le nom de vos environnements, ni leur URL, ni la façon dont vous protégez la
production. Pour ce dernier point, deux réponses conviennent et les deux sont
acceptées : le job attend une main humaine, ou il ne part que sur une étiquette
posée délibérément.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-ep2/pipeline-craft` sur la VM, sur la branche `main`.

La chaîne construit, teste et déploie sans laisser de trace. Quatre traces
manquent, et l'une d'elles bloque les autres.

### Objectif (état attendu)

1. aucun job du dernier pipeline de `main` n'est en attente, et aucun n'a
   échoué ;
2. le projet porte au moins un **environnement**, et au moins un
   **déploiement réussi** y est enregistré ;
3. le **registre** du projet porte au moins une étiquette ;
4. aucun job de production n'est parti de lui-même sur la branche par défaut.

### Aucun indice n'est fourni

C'est une épreuve : les quatre défauts ne sont pas nommés, et il n'y a pas
d'indice à débloquer. Vous avez tout vu dans les quatre labs du niveau.

### Une contrainte de cet environnement

Le registre de cette forge répond en **HTTP**, pas en HTTPS. Un client Docker
refuse par défaut de parler à un registre en clair : le service Docker du job
doit déclarer l'adresse du registre comme non sécurisée. Le pipeline de départ
le fait déjà, c'est un acquis et non un défaut.

### Les commandes qui servent à vérifier

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft

# L'état réel des jobs du dernier pipeline
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/jobs" \
  | jq -r '.[] | "\(.name) \(.status)"'

# Ce que les runners du projet offrent, à comparer avec ce que les jobs demandent
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/runners" \
  | jq -r '.[] | "\(.description) \(.tag_list // [])"'

# Les environnements et les déploiements enregistrés
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/environments" | jq -r '.[] | "\(.name) \(.state)"'
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/deployments" \
  | jq -r '.[] | "\(.environment.name) \(.status) \(.ref)"'

# Les images publiées
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/registry/repositories" | jq -r '.[].id'
```

### Validation

```bash
dsoxlab check gl-ep2-une-livraison-tracable
```
