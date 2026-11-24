# Factoriser le pipeline

## La situation

Le pipeline de `pipeline-craft` marche. Il marche même bien : cache utile, jobs
qui ne s'attendent plus, couverture remontée, image publiée, déploiements en
place.

Il se répète. Deux jobs Python déclarent la même image et le même cache, mot
pour mot. Le bloc de variables Docker est écrit à un seul endroit aujourd'hui,
et le sera à trois quand un deuxième job de construction arrivera.

Rien n'est cassé, et c'est bien le problème : **la duplication ne casse rien
tant que personne ne change une des deux copies**. Le jour où quelqu'un met à
jour l'image dans un job et oublie l'autre, le pipeline continue de passer, et
deux jobs tournent sur deux versions de Python.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Factorisez, sans rien changer au comportement.

Deux mécaniques, et leur différence est la leçon de ce lab :

- **`extends:`** fusionne des **jobs**. C'est un mécanisme de GitLab : il
  comprend les clés qu'il fusionne, il va en profondeur, et il se lit dans
  l'interface. Un **job caché**, dont le nom commence par un point, ne tourne
  jamais seul et existe pour être étendu ;
- **une ancre YAML** recopie un **fragment**, quel qu'il soit. C'est un
  mécanisme du format, pas de GitLab : elle est résolue avant même qu'il ne
  lise le fichier. C'est ce qui permet de factoriser un bloc de variables, qui
  n'est pas un job.

Le lab demande les deux pour que la différence se sente.

## Ce que le lab vérifie, et pourquoi il regarde votre fichier

C'est le **seul lab de la série** dont la note lit le `.gitlab-ci.yml`. Partout
ailleurs, elle porte sur l'état laissé sur la forge. Ici, l'état ne peut pas
servir de mesure, et c'est le sujet même du lab : `extends` et les ancres sont
**résolus** avant l'exécution. La configuration que GitLab produit est
identique avant et après, et c'est précisément ce qu'on vous demande de
vérifier.

1. le fichier porte un **job caché étendu** par au moins un job, et une
   **ancre fusionnée** par `<<:` ;
2. le comportement **n'a pas changé** : les jobs tournent toujours, aucun
   n'échoue, et la couverture remonte encore.

Le second point est celui qui compte le plus. Une factorisation qui change le
comportement n'est pas une factorisation, c'est une régression.

## Un piège qui ne se voit qu'après

`coverage:` appartient au **job**, pas au cache ni à l'image. Si vous déplacez
le job de tests dans un job caché en oubliant cette ligne, le pipeline reste
vert et la couverture disparaît sans un mot. Le lab le vérifie.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-13/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline marche et se répète.

### Objectif (état attendu)

1. Le fichier porte un **job caché** étendu par au moins un job, et une
   **ancre YAML** fusionnée par `<<:`.
2. Le comportement **n'a pas changé** : aucun job en échec, au moins quatre
   jobs réussis, et la couverture remonte toujours.

### Ce qui n'est pas imposé

Ni le nom du job caché, ni celui de l'ancre, ni leur nombre. Deux jobs cachés
et trois ancres conviennent autant qu'un de chaque.

### Deux rappels

- `extends:` fusionne **en profondeur** : un job peut hériter d'un cache et
  n'en redéclarer que la politique ;
- `coverage:` appartient au **job**. Le perdre en déplaçant le job de tests
  laisse le pipeline vert et la couverture vide.

### Validation

```bash
dsoxlab check gl-13-factoriser-le-yaml
```
