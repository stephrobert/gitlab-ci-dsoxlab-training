# Lab: a pipeline that writes its own jobs

A pipeline whose jobs are all written in advance, and a request that does not
fit that mould. Generate a child pipeline during the run, trigger it, and make
the parent wait.

Companion lesson:
[Dynamic pipelines](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-16-pipelines-dynamiques/).

```bash
dsoxlab run gl-16-un-pipeline-enfant
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-16/pipeline-craft (branch main).
dsoxlab challenge gl-16-un-pipeline-enfant
dsoxlab check gl-16-un-pipeline-enfant
```

Grading reads the bridges endpoint: a child that ran, and a trigger job
carrying its status. Without a strategy, the parent goes green as soon as the
child is started, and the child becomes decorative.
