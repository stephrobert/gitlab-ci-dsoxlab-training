# Challenge: make the image traceable, and refuse the ones that are not

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits in
`/opt/dsoxlab/gl-23/pipeline-craft` on the VM, on the `main` branch.

Its pipeline publishes the image to the project registry and stops there.
Another image, `tiers`, sits in the same registry, and nobody has signed it.

## Goal (expected state)

1. The latest healthy pipeline of `main` left a **CycloneDX SBOM** of the image
   in its artifacts.
2. The commit image is **signed** with the project key (`cosign verify` accepts
   it). The private key is neither in the repository nor in a log.
3. A **provenance attestation** (`slsaprovenance`) is attached to the image,
   verifies with the same key, and names the commit.
4. A pipeline **failed** because a verification job refused the `tiers` image for
   lack of a signature, **before any deployment**. The log keeps the reason
   cosign gave.
5. In the latest healthy pipeline, the verification **succeeded before** the
   deployment started.

## Read before you start

Two notes wait next to the repository copy, in `/opt/dsoxlab/gl-23`:

- `REGISTRE-DU-LAB.txt`: the registry answers in HTTP and the project is private;
- `NOTE-SUPPLY-CHAIN.txt`: the `tiers` image, and where the keys are.

## Versions

Syft 1.54.1 and cosign 3.1.3, installed in a job on an Alpine image, as in the
lesson. The jobs and the VM must reach `github.com`.

## Four reminders

- a new stage is **declared** in `stages:`, otherwise GitLab refuses the whole
  configuration and the pipeline is born `failed` with not a single job;
- a signature sits on a **digest**, not on a tag;
- a verification job that throws away cosign's error output does not prove its
  refusal;
- a healthy pipeline ends `manual`, not `success`.

## Validation

```bash
dsoxlab check gl-23-supply-chain-tracable
```
