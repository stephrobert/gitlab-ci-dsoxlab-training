# Scénario

Quelqu'un a modifié le `.gitlab-ci.yml` de `pipeline-craft`, et le pipeline est
rouge. Pas rouge « un job a échoué » : rouge **sans aucun job**. GitLab a
refusé la configuration avant d'en créer un seul.

L'équipe a pris l'habitude de corriger au jugé et de pousser pour voir. Chaque
essai coûte un commit dans l'historique, une place dans la file du runner, et
quelques minutes d'attente. Au troisième aller-retour, personne ne sait plus
quelle version est en ligne.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

Trouvez les défauts **avant** de pousser, puis poussez une fois.

Trois défauts vous attendent, et ils ne sont pas de même nature. C'est cette
différence qui compte, plus que les corrections elles-mêmes :

- le premier fait **refuser** la configuration. GitLab le signale lui-même, et
  son message nomme la cause ;
- le deuxième est **masqué par le premier** : tant que la configuration est
  refusée, rien n'est évalué, donc rien d'autre ne peut être signalé ;
- le troisième, GitLab **l'accepte**. Il ne se voit ni au refus, ni à
  l'exécution. Un fichier accepté n'est pas pour autant un fichier juste.

## Valider sans pousser

GitLab sait dire ce qu'il pense d'une configuration sans l'exécuter :

- l'**éditeur de pipeline** (`Build > Pipeline editor`) valide le fichier de la
  branche choisie et affiche l'erreur ;
- l'**API de lint** répond la même chose en une requête, et rend en plus la
  configuration **fusionnée**, celle que GitLab a réellement comprise après
  résolution des inclusions et des ancres ;
- `glab ci lint`, si vous avez la CLI, fait la même chose depuis le terminal.

## Ce que le lab vérifie

1. GitLab **accepte** la configuration ;
2. plus aucun motif à **trois étoiles** ne subsiste dans la configuration
   fusionnée ;
3. le job de tests a **tourné et réussi**, ce qui ferme les deux premiers
   défauts d'un coup ;
4. le pipeline est **vert**.

Aucun test ne mesure votre méthode : l'état final d'une personne méthodique et
celui d'une personne qui a tâtonné sont identiques. La méthode est le sujet du
lab, pas sa note.
