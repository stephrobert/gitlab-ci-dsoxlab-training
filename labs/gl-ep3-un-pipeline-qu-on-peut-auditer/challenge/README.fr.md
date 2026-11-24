# Épreuve : un pipeline qu'on peut auditer

## La situation

C'est l'épreuve de fin du niveau 4, celui qu'on appelle « Sécuriser ». Il n'y a
pas de pas à pas, pas d'indice, et les défauts ne sont pas nommés.

Un auditeur arrive sur le projet `pipeline-craft` et pose quatre questions :

- **qui peut modifier ce qui part en production, et comment ?**
- **qui peut lire le secret de déploiement ?**
- **qu'est-ce qui tourne exactement dans le pipeline, et quelqu'un l'a-t-il contrôlé ?**
- **pouvez-vous le prouver sans qu'on vous croie sur parole ?**

Le pipeline est vert et le déploiement en production fonctionne. Il ne
survivrait pourtant pas à l'audit : il a été construit pour aller vite, et
personne ne lui a jamais demandé de pouvoir être garanti.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine. L'audit n'est pas un document : c'est un ensemble de réglages que la
forge rapporte, et que n'importe qui, avec un jeton en lecture, peut vérifier
par son API, sans aucune licence payante.

## Mission

Rendre le pipeline **auditable** : cinq promesses ne sont pas tenues, à vous de
les trouver et de les rendre vraies, tandis que le déploiement continue de
fonctionner.

C'est la compétence du niveau. Sécuriser une chaîne n'est pas un outil : c'est
la somme de petites garanties qui tiennent ensemble, et dont chacune peut être
lue par quelqu'un qui ne l'a pas construite. Lisez le projet comme un auditeur
le ferait, depuis l'API.

## Ce que l'épreuve note

Elle note **l'état que la forge rapporte**, jamais les commandes tapées :

1. le secret de déploiement est tenu comme la forge veut qu'un secret le soit ;
2. la branche par défaut ne peut plus être réécrite par n'importe qui ;
3. une demande de fusion ne peut pas être fusionnée sur un pipeline rouge ;
4. ce que les jobs du pipeline téléchargent est épinglé sur une référence
   immuable ;
5. le dernier pipeline de la branche par défaut est sain, il porte des rapports
   de scanners, et le déploiement en production est bien passé.

## Ce que l'épreuve ne note pas

Ni la façon dont vous obtenez un condensat (digest), ni le template de scanner
que vous choisissez. Deux fonctionnalités Premium sont hors périmètre et ne sont
pas demandées : les règles d'approbation et les environnements protégés.

## Ce qui est demandé

### Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt vous attend
dans `/opt/dsoxlab/gl-ep3/pipeline-craft` sur la VM, sur la branche `main`.

Le pipeline est vert et le déploiement en production fonctionne. Cinq promesses
qu'un auditeur demanderait ne sont pas tenues. À vous de trouver lesquelles, et
de les rendre vraies sans casser le déploiement.

### Objectif (état attendu)

1. le secret de déploiement est tenu comme la forge veut qu'un secret le soit ;
2. la branche par défaut ne peut plus être réécrite par n'importe qui ;
3. une demande de fusion ne peut pas être fusionnée sur un pipeline rouge ;
4. ce que les jobs du pipeline téléchargent est épinglé sur une référence
   immuable ;
5. le dernier pipeline de `main` est sain, il porte des rapports de scanners, et
   le déploiement en production est bien passé.

### Aucun indice n'est fourni

C'est une épreuve : les défauts ne sont pas nommés, et il n'y a aucun indice à
débloquer. Vous avez vu chaque geste dans les labs de ce niveau. Tout ce qu'il
faut lire est dans l'API de la forge, et la VM porte un jeton pour elle (voir
la note à côté de la copie du dépôt).

### Validation

```bash
dsoxlab check gl-ep3-un-pipeline-qu-on-peut-auditer
```
