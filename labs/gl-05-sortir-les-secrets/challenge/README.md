# Challenge: get the secret out of the repository

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-05/pipeline-craft` on the VM, on the `main` branch.

A database password sits there in plain text, in two places, and a job prints
it in its log.

## Goal (expected state)

1. The secret is gone from the repository, in `app/config.py` **and** in
   `.gitlab-ci.yml`.
2. The project carries a **masked** CI/CD variable, and a **protected** one if
   the default branch is protected.
3. The secret appears in **no job log** of the latest pipeline.

## Two traps

- GitLab **refuses to mask** a value containing certain characters, and a full
  database URL has them. Declare the **secret alone**, not the address;
- a **protected** variable is only handed to protected branches and tags. If
  your working branch is not protected, the job receives it empty.

## Validation

```bash
dsoxlab check gl-05-sortir-les-secrets
```
