# Lab: publish the image, and keep it traceable

An image built on every run and thrown away with its job. Publish it from the
pipeline, under a tag that names the commit.

Companion lesson:
[Publish to the registry](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-09-publier-registry/).

```bash
dsoxlab run gl-09-publier-au-registre
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-09/pipeline-craft (branch main).
dsoxlab challenge gl-09-publier-au-registre
dsoxlab check gl-09-publier-au-registre
```

Grading reads the project registry, the published tag and the job log. The
heart of the lab is the tag: an image whose name designates no commit cannot be
traced back to the code it runs.
