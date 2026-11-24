# Get the secret out of the repository

## The situation

The `pipeline-craft` pipeline is **green**, and it will stay green whatever you
do. That is exactly the problem: a plain-text secret breaks nothing, it leaks.

A database password sits in **two places** in the repository:

- in `app/config.py`, as the **fallback value** of an environment lookup.
  Handy while developing, and committed forever;
- in `.gitlab-ci.yml`, as a **pipeline variable**, which the test job **prints
  in its log** with an `echo`.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Get that secret out of the repository and out of the logs, without breaking the
pipeline.

Three steps, and the third is the one people forget:

- **remove** the secret from both files. A fallback value never carries a
  secret: a local development database is enough;
- **declare it in the forge**, under `Settings > CI/CD > Variables`. Two
  settings matter: **masked**, so the value never shows up in a log, and
  **protected**, so it is only handed to protected branches and tags;
- **check** that the secret no longer appears in the logs. A log can be
  downloaded by anyone who can see the project.

## What the lab checks

1. the secret is gone from the repository, in `app/config.py` **and** in
   `.gitlab-ci.yml`;
2. a CI/CD variable exists, **masked**, and **protected** if the default branch
   is;
3. the secret appears in **no job log** of the latest pipeline.

No test checks that the pipeline is green: it already was before your work, and
a test that passes without measuring anything is not a test.

## One limit worth knowing

Removing a secret from the default branch does not erase it from the Git
**history**. In real life, a committed secret is a secret **to rotate**: you
change the value, you do not rely on its removal. The lab stops at the step it
can measure; the rule does not stop there.

## What is asked

### Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-05/pipeline-craft` on the VM, on the `main` branch.

A database password sits there in plain text, in two places, and a job prints
it in its log.

### Goal (expected state)

1. The secret is gone from the repository, in `app/config.py` **and** in
   `.gitlab-ci.yml`.
2. The project carries a **masked** CI/CD variable, and a **protected** one if
   the default branch is protected.
3. The secret appears in **no job log** of the latest pipeline.

### Two traps

- GitLab **refuses to mask** a value containing certain characters, and a full
  database URL has them. Declare the **secret alone**, not the address;
- a **protected** variable is only handed to protected branches and tags. If
  your working branch is not protected, the job receives it empty.

### Validation

```bash
dsoxlab check gl-05-sortir-les-secrets
```
