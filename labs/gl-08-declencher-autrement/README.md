# Lab: start a pipeline without a push

A pipeline that only reacts to a push, a regression suite that belongs to the
night, and a neighbouring team that would like to re-run it without an account
on the forge.

Companion lesson:
[Trigger a pipeline](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-08-declencher-pipeline/).

```bash
dsoxlab run gl-08-declencher-autrement
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-08/pipeline-craft (branch main).
dsoxlab challenge gl-08-declencher-autrement
dsoxlab check gl-08-declencher-autrement
```

Grading reads the schedules, the trigger tokens and the pipelines that actually
ran. It compares a non-push pipeline's jobs with a push one's: a job's rules
are not exposed by the API, and that is the only way to prove a source rule
works.
