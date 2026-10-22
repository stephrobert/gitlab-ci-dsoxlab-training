# Lab: reliable without hiding failures

A "failed" pipeline with not a single job, and once repaired, no defences at
all: no timeout, no retry, and two deployments that can start together on the
same environment.

Companion lesson:
[Reliability](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-18-fiabilite/).

```bash
dsoxlab run gl-18-fiabiliser-sans-masquer
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-18/pipeline-craft (branch main).
dsoxlab challenge gl-18-fiabiliser-sans-masquer
dsoxlab check gl-18-fiabiliser-sans-masquer
```

Grading is taken on the deployment locks the forge really created, and on the
configuration as GitLab compiled it: a retry that catches a script failure
fails the lab, because it hides what it should report.
