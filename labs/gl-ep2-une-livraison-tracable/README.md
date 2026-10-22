# Level exam: a delivery you can trace

End of level 2. A chain that builds, tests and deploys without leaving the
slightest trace of what it shipped, and a pipeline that never finishes.

Level plan:
[GitLab CI/CD labs](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/).

```bash
dsoxlab run gl-ep2-une-livraison-tracable
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-ep2/pipeline-craft (branch main).
dsoxlab challenge gl-ep2-une-livraison-tracable
dsoxlab check gl-ep2-une-livraison-tracable
```

Exam with no hints: the four defects are not named, and grading is taken on
what the forge holds, environments, recorded deployments, registry tags and
job states.
