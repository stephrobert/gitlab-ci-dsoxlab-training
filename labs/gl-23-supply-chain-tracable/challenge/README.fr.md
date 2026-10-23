# Challenge : rendre l'image traçable, et refuser celles qui ne le sont pas

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-23/pipeline-craft` sur la VM, sur la branche `main`.

Son pipeline publie l'image dans le registre du projet et s'arrête là. Une autre
image, `tiers`, est dans le même registre, et personne ne l'a signée.

## Objectif (état attendu)

1. Le dernier pipeline sain de `main` a laissé un **SBOM CycloneDX** de l'image
   dans ses artefacts.
2. L'image du commit est **signée** avec la clé du projet (`cosign verify`
   l'accepte). La clé privée n'est ni dans le dépôt ni dans un journal.
3. Une **attestation de provenance** (`slsaprovenance`) est attachée à l'image,
   se vérifie avec la même clé, et nomme le commit.
4. Un pipeline a **échoué** parce qu'un job de vérification a refusé l'image
   `tiers`, faute de signature, **avant tout déploiement**. Le journal garde la
   raison donnée par cosign.
5. Dans le dernier pipeline sain, la vérification a **réussi avant** le début du
   déploiement.

## À lire avant de commencer

Deux notes attendent à côté de la copie du dépôt, dans `/opt/dsoxlab/gl-23` :

- `REGISTRE-DU-LAB.txt` : le registre répond en HTTP et le projet est privé ;
- `NOTE-SUPPLY-CHAIN.txt` : l'image `tiers`, et où sont les clés.

## Versions

Syft 1.54.1 et cosign 3.1.3, installés dans un job sur une Alpine, comme dans la
leçon. Les jobs et la VM doivent atteindre `github.com`.

## Quatre rappels

- une étape nouvelle se **déclare** dans `stages:`, sinon GitLab refuse toute la
  configuration et le pipeline naît `failed` sans un seul job ;
- une signature se pose sur un **digest**, pas sur un tag ;
- un job de vérification qui jette la sortie d'erreur de cosign ne prouve pas
  son refus ;
- un pipeline sain finit `manual`, pas `success`.

## Validation

```bash
dsoxlab check gl-23-supply-chain-tracable
```
