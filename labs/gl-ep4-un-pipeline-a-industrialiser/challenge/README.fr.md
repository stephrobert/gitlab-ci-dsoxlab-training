# Épreuve : un pipeline à industrialiser

## Mission

Le projet `pipeline-craft` est dans la forge du lab, à
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt vous attend
dans `/opt/dsoxlab/gl-ep4/pipeline-craft` sur la VM, sur la branche `main`.

Le pipeline est vert, mais il n'est industrialisé qu'à moitié. Plusieurs choses
qu'une équipe exigerait avant de le réutiliser manquent. À vous de trouver
lesquelles, et de les corriger sans jamais laisser `main` au rouge.

## Objectif (état attendu)

1. les parties communes sont écrites une fois (include ou `extends`) ;
2. les jobs forment un graphe et démarrent sans attendre toute leur étape ;
3. les tests s'exécutent en matrice, chaque instance avec un rapport de test non vide ;
4. un pipeline enfant construit depuis l'artefact d'un job s'exécute et réussit ;
5. le déploiement est verrouillé et borné dans le temps, les relances ne
   couvrent que les pannes système, et un échec transitoire est absorbé ;
6. le dernier pipeline de `main` est vert et résulte de vos changements.

## Aucun indice n'est fourni

C'est une épreuve : les défauts ne sont pas nommés, et il n'y a aucun indice à
débloquer. Vous avez vu chaque geste dans les labs de ce niveau. Tout ce qu'il
faut lire se trouve dans la copie du dépôt et dans l'API de la forge ; la VM
détient un jeton pour elle (voir la note à côté de la copie du dépôt).

## Validation

```bash
dsoxlab check gl-ep4-un-pipeline-a-industrialiser
```
