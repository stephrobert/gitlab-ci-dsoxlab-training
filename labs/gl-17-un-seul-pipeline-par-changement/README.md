# Lab: one change, one pipeline

A runner queue that doubled without a single job being added: every push to a
branch with an open merge request produces two pipelines for the same commit.

Companion lesson:
[Workflows](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-17-workflows/).

```bash
dsoxlab run gl-17-un-seul-pipeline-par-changement
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-17/pipeline-craft (branch main).
dsoxlab challenge gl-17-un-seul-pipeline-par-changement
dsoxlab check gl-17-un-seul-pipeline-par-changement
```

Grading is taken by counting one commit's pipelines: two is the defect; one,
from `merge_request_event`, is the work done.
