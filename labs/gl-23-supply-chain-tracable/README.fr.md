# Lab : signer l'image, et refuser celles qui ne le sont pas

Un pipeline qui publie son image sans rien en dire, et une image `tiers` que
personne n'a signée. Vous inventoriez l'image avec Syft (SBOM CycloneDX), vous la
signez avec cosign, vous attestez sa provenance, puis vous ajoutez une
vérification qui refuse l'image sans signature, et vous le prouvez.

Leçon compagnon :
[GitLab CI : sécuriser la supply chain avec SBOM et attestations](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/securite/supply-chain/).

```bash
dsoxlab run gl-23-supply-chain-tracable
# Le projet est dans la forge du lab : http://gitlab-1.lab/root/pipeline-craft
# Une copie du dépôt attend dans /opt/dsoxlab/gl-23/pipeline-craft (branche main).
dsoxlab challenge gl-23-supply-chain-tracable
dsoxlab check gl-23-supply-chain-tracable
```

La note se prend sur ce que la forge et le registre ont vu : un SBOM CycloneDX
conservé en artefact, une image dont la signature se vérifie avec la clé du
projet, une attestation de provenance, et un pipeline réellement échoué parce que
la vérification a refusé l'image `tiers`. Un `.gitlab-ci.yml` qui déclare un job
`cosign sign` ne prouve rien.

## Ce que vous saurez faire

- générer le SBOM d'une image avec Syft, au format CycloneDX, et le publier en
  artefact ;
- signer une image par son digest avec cosign et une clé gardée dans une variable
  du projet ;
- attacher une attestation de provenance signée à l'image ;
- ajouter un job de vérification qui échoue sur une image non signée, avant le
  déploiement, et le prouver.

Ce lab exige que la VM et les jobs atteignent `github.com` (releases de Syft et
de cosign) et Docker Hub. Il n'utilise aucun service payant ni aucune édition
Premium ou Ultimate de GitLab.
