# Lab: a first pipeline that lints, tests and builds

Make GitLab run what your machine already runs: code style, the test suite and
the image build, as visible stages, and green.

Companion lesson:
[Your first pipeline](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-01-premier-pipeline/).

```bash
dsoxlab run gl-01-premier-pipeline
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-01/pipeline-craft (branch main).
dsoxlab challenge gl-01-premier-pipeline
dsoxlab check gl-01-premier-pipeline
```

Grading reads the pipeline the server really ran, from GitLab's API: its
status, its successful jobs, its stages and those jobs' logs. Neither the job
names nor the contents of your `.gitlab-ci.yml` count towards the score.
