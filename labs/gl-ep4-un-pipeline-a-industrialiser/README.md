# Level exam: a pipeline to industrialise

End of level 3. A green pipeline that was only half industrialised: it runs,
and nobody would want to maintain it or trust it under load.

This exam is not `gl-19-reconstruire-tout-le-pipeline`. That lab builds a
pipeline from a specification, with hints. Here a pipeline already exists, and
you must diagnose what is wrong with it.

Level plan:
[GitLab CI/CD labs](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/).

```bash
dsoxlab run gl-ep4-un-pipeline-a-industrialiser
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-ep4/pipeline-craft (branch main).
dsoxlab challenge gl-ep4-un-pipeline-a-industrialiser
dsoxlab check gl-ep4-un-pipeline-a-industrialiser
```

Exam with no hints: the defects are not named, and grading is taken on the
configuration and the pipeline state the forge reports through its API. No
Premium feature is needed. Expect about 70 minutes.
