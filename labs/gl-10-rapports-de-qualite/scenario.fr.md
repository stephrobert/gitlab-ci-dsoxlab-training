# Scénario

Le pipeline de `pipeline-craft` teste, et il le dit bien : l'onglet Tests du
pipeline liste chaque test, vert ou rouge. C'est l'acquis d'un lab précédent, et
il tient.

Ce qu'il ne dit pas, c'est **combien de code ces tests traversent**. En revue,
la question revient à chaque fois : « est-ce que la partie que tu as modifiée
est testée ? », et personne ne peut répondre sans lancer la suite à la main sur
son poste.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Faites remonter la couverture jusqu'à GitLab, et rendez-la utile.

Deux gestes, et la différence entre eux est tout l'intérêt du lab :

- **le pourcentage.** GitLab ne calcule pas la couverture : il la **lit**. Le
  job doit l'imprimer dans son journal, et une expression régulière déclarée
  sur le job va la pêcher. Le chiffre apparaît alors sur le pipeline, sur le
  job, et dans la demande de fusion ;
- **le rapport.** Un pourcentage dit où l'on en est ; un rapport dit quoi
  faire. Déclaré en artefact de rapport de couverture, il fait apparaître les
  lignes **non couvertes** directement dans le diff d'une demande de fusion.

Sans le second, vous savez que vous couvrez 78 % et vous ignorez lesquels des
22 % vous manquent.

## Ce que le lab vérifie

1. une **couverture** non nulle est arrivée à GitLab, sur le pipeline ou sur un
   job ;
2. un **rapport de couverture** est publié en artefact, et l'acquis tient : le
   rapport de tests est toujours rempli, aucun job n'a échoué.

Le second point porte l'exigence de non-régression, et ce n'est pas un
raccourci : le rapport de tests et la santé du pipeline sont vrais **dès l'état
de départ**, donc des tests séparés passeraient avant tout travail.

## Un piège qui ne dit rien

Une expression régulière qui ne correspond à rien **ne produit aucune erreur**.
Le pipeline reste vert, le job réussit, et le champ de couverture reste vide.
Vérifiez le chiffre après coup, sur la page du pipeline ou par l'API : c'est la
seule façon de savoir que la pêche a pris.
