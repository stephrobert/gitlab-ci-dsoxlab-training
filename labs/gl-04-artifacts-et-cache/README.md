# Lab: dependency cache and test report

A green but wasteful pipeline: every job reinstalls its dependencies, and the
test results vanish with the job. Tell the cache, which avoids rebuilding,
apart from the artifact, which carries a result.

Companion lesson:
[Artifacts and cache](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-04-artifacts-et-cache/).

```bash
dsoxlab run gl-04-artifacts-et-cache
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-04/pipeline-craft (branch main).
dsoxlab challenge gl-04-artifacts-et-cache
dsoxlab check gl-04-artifacts-et-cache
```

Grading reads the pipeline's test report and the job logs: an artifact declared
by its path alone does not fill the Tests tab, and a cache proves nothing until
it has been restored.
