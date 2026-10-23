# Épreuve : un pipeline qu'on peut auditer

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt vous attend
dans `/opt/dsoxlab/gl-ep3/pipeline-craft` sur la VM, sur la branche `main`.

Le pipeline est vert et le déploiement en production fonctionne. Cinq promesses
qu'un auditeur demanderait ne sont pas tenues. À vous de trouver lesquelles, et
de les rendre vraies sans casser le déploiement.

## Objectif (état attendu)

1. le secret de déploiement est tenu comme la forge veut qu'un secret le soit ;
2. la branche par défaut ne peut plus être réécrite par n'importe qui ;
3. une demande de fusion ne peut pas être fusionnée sur un pipeline rouge ;
4. ce que les jobs du pipeline téléchargent est épinglé sur une référence
   immuable ;
5. le dernier pipeline de `main` est sain, il porte des rapports de scanners, et
   le déploiement en production est bien passé.

## Aucun indice n'est fourni

C'est une épreuve : les défauts ne sont pas nommés, et il n'y a aucun indice à
débloquer. Vous avez vu chaque geste dans les labs de ce niveau. Tout ce qu'il
faut lire est dans l'API de la forge, et la VM porte un jeton pour elle (voir
la note à côté de la copie du dépôt).

## Validation

```bash
dsoxlab check gl-ep3-un-pipeline-qu-on-peut-auditer
```
