# Scenario

The `pipeline-craft` pipeline builds an image and publishes it to the project
registry, under the commit tag. That is all. Nobody knows what the image
contains, nothing proves it really comes out of this pipeline, and nothing would
stop a deployment from taking an image that does not.

An incident has just made the point: an image appeared in the project registry,
pushed by another team. It carries the tag `tiers`. If the deployment took it,
nothing would notice.

The project is in the lab forge. A copy of the repository waits on the machine,
with two notes: `REGISTRE-DU-LAB.txt` and `NOTE-SUPPLY-CHAIN.txt`.

## Mission

Five steps. The first three make the image **traceable**, the last two make it
**verifiable**, and those two are what protects.

1. **Inventory the image.** A job reads the image the pipeline has just
   published and builds its SBOM (the list of its components) in **CycloneDX**
   format. The SBOM stays downloadable in the forge.
2. **Sign it.** A job signs the image with the project key. The signature lives
   in the registry, next to the image.
3. **Attest its provenance.** A job attaches a signed attestation to the image:
   which commit, which repository, which pipeline built it.
4. **Verify before deploying.** A job checks the image signature before the
   deploy stage. Without a valid signature it fails and the deployment does not
   start.
5. **Prove the refusal.** A verification that has never failed has never proved
   it can. Point it at the `tiers` image and see it refuse it. Then run a normal
   pipeline again, so that the latest pipeline of `main` is healthy.

## Why external tools, and not a GitLab feature

Syft and cosign do not depend on the GitLab edition: nothing here needs Premium
or Ultimate. They run in a job, like any other tool.

One point is worth making: **cosign can sign without a key** (*keyless* mode),
but it then needs a certificate service (Fulcio) that recognises the issuer of
the pipeline token. A self-hosted GitLab instance is not among them. This lab
therefore signs **with a key pair**, like the lesson: the private key is a
project variable, the public key is a repository file. They are already
generated (see `NOTE-SUPPLY-CHAIN.txt`).

## What the tools must know

| Tool (lesson version) | What you need |
|---|---|
| Syft 1.54.1 | `syft registry:<image> -o cyclonedx-json=<file>` writes the CycloneDX SBOM |
| cosign 3.1.3 | `sign`, `attest --type slsaprovenance`, `verify`, `verify-attestation` |
| crane | `crane digest <image>` gives the digest, the exact content behind a tag |

The official Syft and cosign images contain **no shell**: GitLab cannot run a
job script in them. The lesson starts from an Alpine
(`alpine:3.24.2@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6`)
and installs the tool from its official release, checking its checksum. The jobs
must therefore reach `github.com`.

This forge registry answers in **HTTP**, and the project is **private**: each
tool must be allowed to speak HTTP and to authenticate. The detail, tool by
tool, is in `REGISTRE-DU-LAB.txt`.

## The traps of this lab

- **Sign the digest, not the tag.** A tag is a label that another push can
  move; the digest designates the content. The signature sits on the digest, and
  the verification must read the same one.
- **A failing job must say why.** If your script throws away cosign's error
  output, an unreachable registry looks like a missing signature, and nobody
  will know whether the refusal is real. The job log must name the refused image
  and keep the reason cosign gave.
- **The verification must be able to target another image than the commit's.**
  Otherwise you cannot present `tiers` to it.
- **A new stage is declared in `stages:`.** Otherwise GitLab refuses the whole
  configuration: the pipeline is born `failed`, with not a single job, and the
  page does not say why.
- **The private key is written nowhere.** Not in the repository, not in a log. A
  printed key is a key everybody has.
- **A healthy pipeline ends `manual`**, not `success`: the production deployment
  waits for a hand. That is normal.

## What the lab checks

1. the latest healthy pipeline of `main` left a **CycloneDX SBOM** as an
   artifact, describing this project's image, with its components;
2. the commit image is **signed**: `cosign verify`, run by the test against the
   registry with the project public key, accepts it. The private key is neither
   in the repository nor in a log;
3. a **provenance attestation** (`slsaprovenance`) verifies with the same key,
   and its content names the commit;
4. a pipeline **really failed** because a verification job refused the `tiers`
   image for lack of a signature, **before any deployment**;
5. in the latest healthy pipeline, a job that ran `cosign verify` succeeded and
   finished **before** the deployment started.

## What the lab does not check

Neither the name of your jobs, nor of your stages, nor of the SBOM file, nor of
the variable that designates the image to verify. Nor the quality of your
attestation beyond its signature and the commit it names.

## Checking by hand

Job artifacts can be read in the project interface. To see the pipelines from
the VM:

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=5" \
  | jq -r '.[] | "\(.id) \(.status) \(.sha[0:8])"'
```

The project public key is in the repository (`cosign.pub`). You can also verify
an image yourself, from the VM, with the script the setup left:

```bash
sudo /var/lib/dsoxlab/gl-23-cles/cosign-registre.sh verify \
  --key /var/lib/dsoxlab/gl-23-cles/cosign.pub --insecure-ignore-tlog=true \
  --allow-http-registry gitlab-1.lab:5050/root/pipeline-craft:tiers
```

An unsigned image answers `no signatures found`.
