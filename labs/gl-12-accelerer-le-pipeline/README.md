# Lab: make the pipeline faster

A cache that is declared, created on every run, and only ever serves once: its
key changes on every commit, so it never crosses two commits. And jobs waiting
for a stage they do not need.

Companion lesson:
[Speed up the pipeline](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-12-accelerer-pipeline/).

```bash
dsoxlab run gl-12-accelerer-le-pipeline
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-12/pipeline-craft (branch main).
dsoxlab challenge gl-12-accelerer-le-pipeline
dsoxlab check gl-12-accelerer-le-pipeline
```

Grading is not about a duration, which varies with the machine's load: it is
about the two mechanics that bring it down: a cache key that is stable from
one pipeline to the next, and two jobs overlapping in time.
