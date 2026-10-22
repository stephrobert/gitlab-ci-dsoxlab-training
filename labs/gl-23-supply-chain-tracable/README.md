# Lab: sign the image, and refuse the ones that are not

A pipeline that publishes its image without saying anything about it, and a
`tiers` image nobody has signed. You inventory the image with Syft (CycloneDX
SBOM), sign it with cosign, attest its provenance, then add a verification that
refuses an image without a signature, and you prove it.

Companion lesson:
[GitLab CI: securing the supply chain with SBOMs and attestations](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/securite/supply-chain/).

```bash
dsoxlab run gl-23-supply-chain-tracable
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-23/pipeline-craft (main branch).
dsoxlab challenge gl-23-supply-chain-tracable
dsoxlab check gl-23-supply-chain-tracable
```

The grade is taken on what the forge and the registry saw: a CycloneDX SBOM kept
as an artifact, an image whose signature verifies with the project key, a
provenance attestation, and a pipeline that really failed because the
verification refused the `tiers` image. A `.gitlab-ci.yml` that declares a
`cosign sign` job proves nothing.

## What you will be able to do

- generate an image SBOM with Syft, in CycloneDX format, and publish it as an
  artifact;
- sign an image by its digest with cosign and a key kept in a project variable;
- attach a signed provenance attestation to the image;
- add a verification job that fails on an unsigned image, before the deployment,
  and prove it.

This lab requires the VM and the jobs to reach `github.com` (Syft and cosign
releases) and Docker Hub. It uses no paid service and no GitLab Premium or
Ultimate edition.
