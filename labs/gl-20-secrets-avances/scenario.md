# Scenario

The `pipeline-craft` pipeline is **green**, and it will stay green whatever you
do with its secrets. That is precisely the problem: a badly stored secret breaks
nothing, it is exposed.

Two secrets live in the project CI/CD variables:

- **`SERVICE_TOKEN`**, a project access token (`service-v1`) that the
  `joindre-le-service` job uses to call the forge API. The variable is neither
  protected nor masked;
- **`DEPLOY_KEY`**, a multi-line SSH deployment key. The variable is an ordinary
  one, and the `installer-la-cle` job copies it by hand into a file.

The `main` branch is protected. The project is in the lab forge. A copy of the
repository waits on the machine, with a note: `NOTE-SECRETS.txt`.

## Mission

Three steps, and the third is the one that always gets postponed.

1. **Protect and mask the service token.** A protected variable is only handed to
   pipelines of protected branches; a masked variable is replaced by `[MASKED]`
   in job logs.
2. **Turn the deployment key into a file-type variable.** The job no longer
   receives the value, it receives the **path** of a file that holds it. You must
   change the variable type **and** adapt the job, without breaking it. The key
   must stay protected.
3. **Renew the service token without interrupting the service.** Token
   `service-v1` is considered compromised. Put a **new** token in service, prove
   with a pipeline that it works, and **only then** revoke the old one. A secret
   removed before its replacement is in place cuts the service; an old secret
   never revoked stays valid for whoever copied it.

## What the lab checks

1. `SERVICE_TOKEN` is **protected and masked** in the forge;
2. `DEPLOY_KEY` is **file-type**, protected, and its value is intact;
3. the old token is **revoked**, the variable holds **another valid token**, and
   the `joindre-le-service` job has **never failed** since the start, while having
   succeeded with the new token;
4. the latest pipeline on `main` is **healthy**, both jobs succeed, and the log
   of `installer-la-cle` shows `CLE-SOURCE=fichier`: the job really received the
   key as a file. That line is written by the starting job: keep it when you adapt
   the job.

Both jobs keep their name. The lab reads the settings the forge holds and what its
jobs did, never the content of `.gitlab-ci.yml`.

Keeping a secret out of a log is the subject of the `gl-05-sortir-les-secrets`
lab: here, the runner masks `glpat-` tokens by itself, so that topic is not played.

## A limit to know

The forge does not date the revocation of a token: the lab cannot prove that your
new token was serving **before** you revoked the old one. It checks what can be
measured, and keeping the order is up to you. In real life the same rule holds
for any secret: install the new one, verify, then revoke.

## Vault

A secrets manager such as Vault can issue short-lived secrets and renew them by
itself. It is **optional** here: this lab does not need it and does not install it.
