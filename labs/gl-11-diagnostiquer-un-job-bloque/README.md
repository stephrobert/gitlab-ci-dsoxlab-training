# Lab: two silent failures

A push that produces no pipeline, then a job that waits forever without
failing. Two failures with no message, the most expensive kind to diagnose.

Companion lesson:
[Debug a stuck job](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-11-debugger-job-bloque/).

```bash
dsoxlab run gl-11-diagnostiquer-un-job-bloque
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-11/pipeline-craft (branch main).
dsoxlab challenge gl-11-diagnostiquer-un-job-bloque
dsoxlab check gl-11-diagnostiquer-un-job-bloque
```

Grading reads the pipeline left on the forge: its existence first, then the
absence of stuck jobs and the linter's trace. A `manual` job is not a stuck
job.
