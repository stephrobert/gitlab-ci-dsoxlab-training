# Lab: the right image for each job

Three jobs on one full Python image, one of which tries to build a Docker
image. Pick the image that matches each piece of work, and give the build job a
daemon.

Companion lesson:
[Images and runners](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-03-images-et-runners/).

```bash
dsoxlab run gl-03-images-et-runners
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-03/pipeline-craft (branch main).
dsoxlab challenge gl-03-images-et-runners
dsoxlab check gl-03-images-et-runners
```

Grading reads the job logs, where GitLab Runner records the image it pulled:
green pipeline, a completed `docker build`, a Docker service started, and no
job left on the full `python:3.12`.
