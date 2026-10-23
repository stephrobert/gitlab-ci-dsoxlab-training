# Exam: a pipeline you can audit

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-ep3/pipeline-craft` on the VM, on branch `main`.

The pipeline is green and the production deployment works. Five promises that
an auditor would ask for are not kept. It is up to you to find which, and to
make them true without breaking the deployment.

## Goal (expected state)

1. the deployment secret is held as the forge would want a secret held;
2. the default branch can no longer be rewritten by just anyone;
3. a merge request cannot be merged on a red pipeline;
4. what the pipeline's own jobs pull is pinned to an immutable reference;
5. the latest pipeline of `main` is healthy, shows scanner reports, and the
   production deployment went through.

## No hints are provided

This is an exam: the defects are not named, and there is no hint to unlock. You
have seen every gesture in the labs of this level. Everything you need to read
is in the forge API, and the VM holds a token for it (see the note next to the
repository copy).

## Validation

```bash
dsoxlab check gl-ep3-un-pipeline-qu-on-peut-auditer
```
