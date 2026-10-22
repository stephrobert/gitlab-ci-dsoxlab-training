# Scénario

Le dépôt est là, l'application tourne, les tests existent, le `Dockerfile` est
prêt. Il n'y a plus de pipeline.

Pas un pipeline cassé : pas de pipeline du tout. Ni `.gitlab-ci.yml`, ni
répertoire `ci/`, ni script de génération. Ce qui reste est un **cahier des
charges**, dans `CAPSTONE-LAB-19.md` à la racine du dépôt, et une forge qui
attend.

C'est l'épreuve de synthèse du parcours. Aucun pas à pas : ce que vous avez
appris lab après lab doit maintenant tenir ensemble dans un seul pipeline.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Reconstruire un pipeline qui répond au cahier des charges. Sept exigences, et
elles se recoupent :

1. **cinq étapes** : analyse, test, orchestration, construction, déploiement ;
2. une **CI modulaire** : les jobs vivent dans plusieurs fichiers inclus, pas
   dans un seul long fichier ;
3. une **matrice** de tests sur Python 3.11 et 3.12, dont les résultats
   **remontent** dans GitLab ;
4. un **pipeline enfant dynamique**, généré pendant l'exécution et déclenché
   depuis un artefact ;
5. une image **construite et publiée** au registre, avec des dépendances
   explicites ;
6. un `workflow:` qui gère la demande de fusion, la branche par défaut et les
   étiquettes ;
7. des déploiements **fiables** : exclusivité, délai, relance ciblée.

## Ce que l'épreuve note, et ce qu'elle ne note pas

Elle note **l'état que la forge montre** : les étapes d'un pipeline qui a
tourné, les fichiers que GitLab a réellement inclus, les instances de la
matrice, les cas de test remontés, le pipeline enfant déclenché, les étiquettes
posées dans le registre, les verrous de déploiement créés.

Elle ne note **aucun nom de job**, aucun nombre de fichiers, aucune version
d'image, aucune valeur de délai. Il y a plus d'une bonne réponse, et le corrigé
en est une, pas la seule.

Une seule exigence du cahier des charges n'est pas mesurée directement : les
trois contextes du `workflow:`. Les vérifier demanderait d'ouvrir une demande de
fusion et de poser une étiquette, ce que le lab sur les workflows mesure déjà.
Ici, le `workflow:` est jugé par ce qu'il produit : un pipeline qui naît sur la
branche par défaut.

## Deux pièges qui ont leur propre lab

Vous les avez rencontrés, et ils reviendront dans cet ordre.

**Un pipeline refusé ne ressemble pas à un pipeline en échec.** GitLab compile
toute la configuration avant de créer le moindre job : un seul défaut quelque
part, et il n'en crée aucun. La page affiche « failed » sans un seul job, et le
champ réservé aux erreurs de configuration reste vide. Seul le **linter CI** du
projet nomme la cause.

**Un artefact n'est pas un résultat.** Un `pytest` qui écrit son fichier XML
sans le déclarer comme rapport laisse un fichier téléchargeable et rien
d'autre : ni compte de tests dans le pipeline, ni rien dans la demande de
fusion.

## Une contrainte de cet environnement, à connaître avant de commencer

Le registre de cette forge répond en **HTTP**, pas en HTTPS. Un client Docker
refuse par défaut de parler à un registre en clair, et le job de construction
échouerait sans explication utile. Le mémo `REGISTRE-DU-LAB.txt`, posé à côté
de votre copie de travail, donne la ligne exacte à écrire.

Ce n'est pas une bizarrerie de lab : un registre interne en HTTP impose la même
chose en entreprise. En production, le registre est servi en HTTPS et la
contrainte disparaît.
