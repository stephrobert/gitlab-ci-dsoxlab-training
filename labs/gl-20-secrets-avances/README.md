# Lab: secrets that are renewed without breaking the pipeline

A green pipeline that uses a token neither protected nor masked, and an SSH key
copied by hand into a file. You protect and mask the token, turn the key into a file-type
variable, then renew the token without interrupting the service: the new one
first, proof by a pipeline, revocation of the old one afterwards.

Companion lesson:
[Secrets management in GitLab CI](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/securite/secrets/).

```bash
dsoxlab run gl-20-secrets-avances
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-20/pipeline-craft (branch main).
dsoxlab challenge gl-20-secrets-avances
dsoxlab check gl-20-secrets-avances
```

Grading is based on the state the forge holds: variable settings, active or
revoked access tokens, executed jobs, logs. A `.gitlab-ci.yml` that mentions a
protected variable proves nothing about it.

## What you will be able to do

- protect and mask a CI/CD variable, and say what each setting changes;
- turn a multi-line secret into a file-type variable and adapt the job;
- renew a secret without interruption: create the new one, put it in service,
  prove it, then revoke the old one.

This lab needs no Vault, no paid service and no Premium or Ultimate GitLab
edition: project access tokens exist in Community Edition.
