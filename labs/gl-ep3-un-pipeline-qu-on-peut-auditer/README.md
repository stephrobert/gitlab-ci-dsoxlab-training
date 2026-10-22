# Level exam: a pipeline you can audit

End of level 4. A green pipeline that deploys to production, and that nobody
could vouch for before an auditor.

Level plan:
[GitLab CI/CD labs](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/).

```bash
dsoxlab run gl-ep3-un-pipeline-qu-on-peut-auditer
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-ep3/pipeline-craft (branch main).
dsoxlab challenge gl-ep3-un-pipeline-qu-on-peut-auditer
dsoxlab check gl-ep3-un-pipeline-qu-on-peut-auditer
```

Exam with no hints: the defects are not named, and grading is taken on the
settings and the pipeline state the forge reports through its API. No Premium
feature is needed.
