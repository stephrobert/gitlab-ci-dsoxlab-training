# Scénario

Le pipeline de `pipeline-craft` construit une image et la publie dans le
registre du projet, sous le tag du commit. C'est tout. Personne ne sait ce que
cette image contient, rien ne prouve qu'elle sort bien de ce pipeline, et rien
n'empêcherait de déployer une image qui n'en sort pas.

Un incident vient de le rappeler : une image est apparue dans le registre du
projet, poussée par une autre équipe. Elle porte le tag `tiers`. Si le
déploiement la prenait, rien ne le verrait.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine, avec deux notes : `REGISTRE-DU-LAB.txt` et `NOTE-SUPPLY-CHAIN.txt`.

## Mission

Cinq temps. Les trois premiers rendent l'image **traçable**, les deux derniers
la rendent **vérifiable**, et c'est eux qui protègent.

1. **Inventorier l'image.** Un job lit l'image que le pipeline vient de
   publier et en dresse le SBOM (la liste de ses composants) au format
   **CycloneDX**. Le SBOM reste téléchargeable dans la forge.
2. **La signer.** Un job signe l'image avec la clé du projet. La signature
   vit dans le registre, à côté de l'image.
3. **Attester sa provenance.** Un job attache à l'image une attestation
   signée : quel commit, quel dépôt, quel pipeline l'a construite.
4. **Vérifier avant de déployer.** Un job contrôle la signature de l'image
   avant l'étape de déploiement. Sans signature valide, il échoue et le
   déploiement ne part pas.
5. **Prouver le refus.** Une vérification qui n'a jamais échoué n'a jamais
   prouvé qu'elle savait le faire. Faites-la porter sur l'image `tiers` et
   constatez qu'elle la refuse. Puis relancez un pipeline normal, pour que le
   dernier pipeline de `main` soit sain.

## Pourquoi des outils externes, et pas une fonction de GitLab

Syft et cosign sont indépendants de l'édition de GitLab : rien ici ne demande
Premium ni Ultimate. Ils tournent dans un job, comme n'importe quel outil.

Un point mérite d'être dit : **cosign sait signer sans clé** (le mode
*keyless*), mais il lui faut alors un service d'émission de certificats
(Fulcio) qui reconnaisse l'émetteur du jeton du pipeline. Une instance GitLab
auto-hébergée n'y figure pas. Ce lab signe donc **avec une paire de clés**, comme
la leçon : la clé privée est une variable du projet, la clé publique est un
fichier du dépôt. Elles sont déjà générées (voir `NOTE-SUPPLY-CHAIN.txt`).

## Ce que les outils doivent savoir

| Outil (version de la leçon) | Ce dont vous avez besoin |
|---|---|
| Syft 1.54.1 | `syft registry:<image> -o cyclonedx-json=<fichier>` écrit le SBOM CycloneDX |
| cosign 3.1.3 | `sign`, `attest --type slsaprovenance`, `verify`, `verify-attestation` |
| crane | `crane digest <image>` donne le digest, le contenu exact d'un tag |

Les images officielles de Syft et de cosign ne contiennent **aucun shell** :
GitLab ne peut pas y lancer le script d'un job. La leçon part d'une Alpine
(`alpine:3.24.2@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6`)
et installe l'outil depuis sa release officielle, en vérifiant son empreinte.
Les jobs doivent donc atteindre `github.com`.

Le registre de cette forge répond en **HTTP**, et le projet est **privé** :
chaque outil doit être autorisé à parler HTTP et s'authentifier. Le détail, outil
par outil, est dans `REGISTRE-DU-LAB.txt`.

## Les pièges de ce lab

- **Signer le digest, pas le tag.** Un tag est une étiquette qu'un autre push
  peut déplacer ; le digest désigne le contenu. La signature se pose sur le
  digest, et la vérification doit lire le même.
- **Un job qui échoue doit dire pourquoi.** Si votre script jette la sortie
  d'erreur de cosign, un registre injoignable ressemble à une absence de
  signature, et personne ne saura si le refus est réel. Le journal du job doit
  nommer l'image refusée et garder la raison donnée par cosign.
- **La vérification doit pouvoir viser une autre image que celle du commit.**
  Sinon, vous ne pouvez pas lui présenter `tiers`.
- **Une étape nouvelle se déclare dans `stages:`.** Sinon GitLab refuse toute la
  configuration : le pipeline naît `failed`, sans un seul job, et la page ne dit
  pas pourquoi.
- **La clé privée ne s'écrit nulle part.** Ni dans le dépôt, ni dans un journal.
  Une clé affichée est une clé que tout le monde a.
- **Un pipeline sain finit `manual`**, pas `success` : le déploiement de
  production attend une main. C'est normal.

## Ce que le lab vérifie

1. le dernier pipeline sain de `main` a laissé en artefact un **SBOM
   CycloneDX** qui décrit l'image de ce projet, avec ses composants ;
2. l'image du commit est **signée** : `cosign verify`, lancé par le test
   sur le registre avec la clé publique du projet, l'accepte. La clé privée n'est
   ni dans le dépôt ni dans un journal ;
3. une **attestation de provenance** (`slsaprovenance`) se vérifie avec la même
   clé, et son contenu nomme le commit ;
4. un pipeline a **réellement échoué** parce qu'un job de vérification a
   refusé l'image `tiers`, faute de signature, **avant tout déploiement** ;
5. dans le dernier pipeline sain, un job qui a lancé `cosign verify` a réussi et
   s'est terminé **avant** le début du déploiement.

## Ce que le lab ne vérifie pas

Ni le nom de vos jobs, ni celui de vos étapes, ni celui du fichier de SBOM, ni
celui de la variable qui désigne l'image à vérifier. Ni la qualité de votre
attestation au-delà de sa signature et du commit qu'elle nomme.

## Vérifier à la main

Les artefacts d'un job se lisent dans l'interface du projet. Pour voir l'état
des pipelines depuis la VM :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=5" \
  | jq -r '.[] | "\(.id) \(.status) \(.sha[0:8])"'
```

La clé publique du projet est dans le dépôt (`cosign.pub`). Vous pouvez aussi
vérifier une image vous-même, depuis la VM, avec le script que le setup a posé :

```bash
sudo /var/lib/dsoxlab/gl-23-cles/cosign-registre.sh verify \
  --key /var/lib/dsoxlab/gl-23-cles/cosign.pub --insecure-ignore-tlog=true \
  --allow-http-registry gitlab-1.lab:5050/root/pipeline-craft:tiers
```

Une image sans signature répond `no signatures found`.
