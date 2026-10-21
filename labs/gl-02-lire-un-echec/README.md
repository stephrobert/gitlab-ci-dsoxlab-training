# Lab: read a pipeline failure and fix it

A red pipeline, three bugs, and their clues in GitLab's messages. Diagnose
before fixing, instead of re-running "just in case".

Companion lesson:
[Read a failure and fix it](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-02-lire-un-echec/).

```bash
dsoxlab run gl-02-lire-un-echec
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-02/pipeline-craft (branch main).
dsoxlab challenge gl-02-lire-un-echec
dsoxlab check gl-02-lire-un-echec
```

Grading measures the **three fixes**, not just the final green: configuration
accepted by GitLab, unused imports gone from the repository, green pipeline,
and the trace of both lint and tests in the logs.
