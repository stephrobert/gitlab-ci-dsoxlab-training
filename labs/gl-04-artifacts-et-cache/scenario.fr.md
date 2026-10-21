# Scénario

Le pipeline de `pipeline-craft` est **vert**, et il le reste. Rien à réparer
cette fois : il y a du gaspillage à supprimer et un résultat à rendre
exploitable.

Deux constats que l'équipe fait chaque jour :

- **chaque job retélécharge ses dépendances** depuis zéro. Trois jobs, trois
  installations de paquets Python identiques, à chaque passage ;
- **les résultats des tests disparaissent** avec le job. Quand un test casse,
  il faut ouvrir le journal et le lire à la main : l'onglet Tests du pipeline
  est vide, parce que rien ne le remplit.

Le projet est dans la forge du lab, avec son pipeline vert. Une copie du dépôt
vous attend sur la machine.

## Mission

Supprimez le gaspillage et rendez les résultats lisibles.

Deux mécanismes, souvent confondus, et la différence est la leçon de ce lab :

- le **cache** sert à retrouver, d'un passage à l'autre, ce qu'il serait
  coûteux de refabriquer. Il est **optimiste** : s'il manque, le job marche
  quand même, juste plus lentement. Sa clé décide de sa durée de vie ;
- l'**artefact** sert à transmettre un résultat : à un job suivant, à un
  humain qui le télécharge, ou à GitLab lui-même quand c'est un rapport.

## Ce que le lab vérifie

1. le dernier pipeline de la branche par défaut est **vert** ;
2. le **rapport de tests du pipeline** est rempli, et sans échec. Un artefact
   déclaré par son seul chemin est téléchargeable mais jamais lu : il faut
   le déclarer comme rapport ;
3. un cache a été **créé** ;
4. un cache a été **restauré** au moins une fois.

Le point 4 demande **deux passages** : un cache se crée au premier et ne se
restaure qu'au suivant. C'est aussi l'occasion de comparer les durées.
