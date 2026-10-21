# Lab: get the secret out of the repository

A plain-text password in two places, and a job that prints it. Remove it,
declare it masked and protected in the forge, and prove it no longer leaks.

Companion lesson:
[Get the secrets out](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-05-sortir-les-secrets/).

```bash
dsoxlab run gl-05-sortir-les-secrets
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-05/pipeline-craft (branch main).
dsoxlab challenge gl-05-sortir-les-secrets
dsoxlab check gl-05-sortir-les-secrets
```

Grading reads the repository, the project's CI/CD variables and the job logs.
The tests never read a variable's **value**: a failure message carrying it
would publish the secret.
