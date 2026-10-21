# Scenario

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
