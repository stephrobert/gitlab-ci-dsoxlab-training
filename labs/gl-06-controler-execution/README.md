# Lab: decide when the pipeline runs, and who deploys

Every job runs on every push, and nothing is deployed. Set a global
`workflow:`, per-job `rules:`, an automatic staging deployment and a manual
production one.

Companion lesson:
[Control execution](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-06-controler-execution/).

```bash
dsoxlab run gl-06-controler-execution
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-06/pipeline-craft (branch main).
dsoxlab challenge gl-06-controler-execution
dsoxlab check gl-06-controler-execution
```

Grading reads the pipeline's state: one successful deployment, one waiting for
a decision, and no failed job. The pipeline's status will be `manual`
while production waits: that is the intended state. The `workflow:` block is the only point read from
the configuration GitLab understood, for lack of an observable effect without
pushing a branch.
