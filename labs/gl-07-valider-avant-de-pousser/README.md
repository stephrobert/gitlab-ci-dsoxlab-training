# Lab: validate before you push

A refused pipeline, a fault the refusal hides, and a third one GitLab accepts
without a word. Find them without pushing to see.

Companion lesson:
[Validate a pipeline](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-07-valider-pipeline/).

```bash
dsoxlab run gl-07-valider-avant-de-pousser
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-07/pipeline-craft (branch main).
dsoxlab challenge gl-07-valider-avant-de-pousser
dsoxlab check gl-07-valider-avant-de-pousser
```

Grading reads the configuration GitLab accepted and the jobs that ran. It does
not measure the method: the end state of a methodical person and that of
someone who guessed are identical.
