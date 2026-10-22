# Scénario

Le pipeline de `pipeline-craft` est **vert**. Il lance un job `tester`, puis deux
jobs qui jouent chacun une attaque contre le runner qui les exécute :

- `attaque-privilege` tente de monter un système de fichiers depuis le job. Cela
  exige un conteneur privilégié, et le job affiche `ATTAQUE-REUSSIE` ;
- `attaque-image` exécute une image (`alpine:3.20`) que personne n'a validée, et
  affiche lui aussi `ATTAQUE-REUSSIE`.

Les deux jobs sont verts parce que **les attaques fonctionnent**. Un job d'attaque
vert est le problème, pas la bonne nouvelle. Ils portent `allow_failure: true` : une
attaque bloquée (un job en échec) ne fait pas passer tout le pipeline au rouge.

On ne durcit pas un runner avec une ligne de `.gitlab-ci.yml`. C'est une
**configuration que le runner détient**, dans `/etc/gitlab-runner/config.toml` sur la
VM, un fichier qui appartient à root. Le projet est dans la forge du lab. Une copie du
dépôt vous attend sur la machine, avec une note : `NOTE-RUNNER.txt`.

## Mission

Trois durcissements, puis une preuve.

1. **Plus de mode privilégié.** Un job ne doit plus détenir un accès root complet à l'hôte.
2. **N'autoriser que les images utilisées.** Le pipeline légitime utilise
   `alpine:3.24.2@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6`
   et doit continuer à tourner. `alpine:3.20` doit être refusée. Une clé absente
   autorise toute image, et un joker seul n'est pas une liste.
3. **Retirer les capacités Linux et interdire le gain de privilège.** Retirez-les
   toutes, et ajoutez l'option qui empêche un processus de gagner des privilèges.
4. **Le prouver.** Lancez un pipeline sur `main` et attendez-le. `tester` doit
   réussir, et les deux jobs d'attaque doivent avoir **échoué sur le refus**, avec la
   raison dans leur journal.

Ne modifiez pas `.gitlab-ci.yml` : les attaques sont la mesure.

## Ce que le lab vérifie

1. le runner n'est pas privilégié ;
2. `allowed_images` existe, laisse passer l'image légitime et refuse `alpine:3.20` ;
3. `cap_drop` contient `ALL` et `security_opt` contient `no-new-privileges:true` ;
4. un pipeline a tourné sur `main` depuis le début, et `tester` a réussi ;
5. dans ce pipeline, `attaque-privilege` a échoué et son journal dit que l'attaque a été bloquée ;
6. dans ce pipeline, `attaque-image` a échoué et le runner a refusé l'image.

Le lab lit la configuration du runner et les journaux des jobs. Il n'impose pas les
motifs que vous écrivez, tant qu'ils couvrent l'image légitime et pas celle de
l'attaque.

## Deux limites à connaître

Un runner durci **ne construit plus d'image avec Docker-in-Docker**, qui exige
`privileged = true`. Le lab ne rejoue pas de build ; la leçon explique les
alternatives. Et le lab n'essaie pas toutes les évasions : il en rejoue deux, et un
runner qui les bloque n'est pas pour autant prouvé sûr.
