# Scénario

Le pipeline est rouge, et personne ne comprend pourquoi.

La page du pipeline affiche **« failed »** et **aucun job**. Pas un job en
échec : pas un job du tout. Le journal est vide, il n'y a rien à ouvrir, et
l'API interrogée sur les erreurs de la configuration répond `null`. Le dernier
commit touchait l'orchestration ajoutée au lab précédent.

Et une fois ce premier problème réglé, il en reste un second, moins visible
mais plus coûteux : ce pipeline n'a **aucune défense**. Aucun job n'est borné
dans le temps, aucun ne se relève d'une panne de runner, et les deux
déploiements peuvent partir en même temps sur le même environnement.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Deux temps, et le premier commande le second.

1. **Réparer ce qui empêche tout.** Tant que GitLab refuse la configuration,
   il n'y a pas de pipeline, donc rien à fiabiliser.
2. **Fiabiliser sans masquer.** Une relance, des délais, un verrou de
   déploiement.

## Pourquoi un pipeline sans un seul job

GitLab compile toute la configuration avant de créer le moindre job. Un seul
défaut quelque part, et il n'en crée aucun : le pipeline naît déjà perdu.

Le piège est que la page du pipeline ne dit pas lequel. Le champ que l'API
réserve aux erreurs de configuration reste vide, et l'interface se contente du
mot « failed ». Un seul endroit nomme la cause : le **linter CI** du projet,
qui compile la configuration d'une branche et rend ses erreurs en clair. C'est
le même réflexe que le lab de diagnostic : quand le pipeline ne parle pas, on
demande à celui qui compile.

## Le piège de la fiabilité, et c'est tout le lab

Relancer un job qui échoue paraît la bonne réponse à tout. C'est faux, et c'est
la seule occasion de ce parcours où un réglage de fiabilité rend un pipeline
**moins** fiable.

Un job échoue pour deux familles de raisons qui n'ont rien en commun :

- **le runner tombe, l'API ne répond pas, le job reste en attente faute de
  runner libre.** Rien n'était faux. Rejouer est exactement la bonne réponse ;
- **le script échoue.** Quelque chose est faux. Rejouer ne fait que reporter le
  diagnostic, et un test instable finit par passer **au hasard**. La relance
  masque alors précisément ce qu'on lui demande de signaler, et l'équipe perd
  sa confiance dans le vert.

Une relance se **cible** donc sur les raisons d'infrastructure. Le mot-clé de
GitLab le permet, à condition de nommer les raisons une par une.

## Un déploiement n'est pas une construction

Le fichier principal pose, pour tous les jobs, l'autorisation d'être annulé
quand un nouveau commit arrive. Pour une construction, c'est une économie :
annulée, elle ne laisse rien derrière elle.

Pour un déploiement, c'est un danger. Interrompu au milieu, il laisse
l'environnement dans un état que personne n'a décrit : la moitié des fichiers
copiés, le service redémarré ou pas. Un déploiement se mène jusqu'au bout.

Même raisonnement pour deux déploiements qui partent ensemble sur le même
environnement : le dernier parti n'est pas forcément le dernier arrivé, et
l'environnement garde la version de celui qui a fini le dernier. GitLab sait
sérialiser deux jobs sous un **verrou nommé** : le second attend que le premier
rende le verrou.

## Ce que le lab vérifie

1. chaque déploiement porte un **verrou**, et la forge a réellement **créé**
   ces verrous : un réglage qui ne produit aucun objet côté serveur n'a pas
   pris effet ;
2. une **relance existe**, et **aucune ne rattrape un échec de script** ;
3. les déploiements portent un **délai** et ne sont **plus annulables**, délai
   et interruption lus dans la configuration telle que **GitLab l'a compilée**,
   héritages résolus.

## Ce que le lab ne vérifie pas

Ni le nom de vos verrous, ni la valeur de vos délais, ni la liste exacte des
raisons de relance que vous retenez. Il y a plus d'une bonne réponse, et c'est
la propriété qui compte, pas la recette.
