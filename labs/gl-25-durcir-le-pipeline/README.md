# Lab: harden the runner, and close what was wide open

A pipeline runs on a runner that is wide open, and it replays two attacks against
it: both succeed. You harden the runner configuration, run the pipeline again,
and prove the two attacks are now blocked while the legitimate job still passes.

Companion lesson:
[GitLab CI: harden your pipelines in 10 measures](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/securite/durcissement/).

```bash
dsoxlab run gl-25-durcir-le-pipeline
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-25/pipeline-craft (main branch).
dsoxlab challenge gl-25-durcir-le-pipeline
dsoxlab check gl-25-durcir-le-pipeline
```

The grade is taken on the runner configuration (`/etc/gitlab-runner/config.toml`)
and on the logs of the jobs the pipeline ran. Nothing in `.gitlab-ci.yml` hardens a
runner.

## What you will be able to do

- say what `privileged = true` gives a job, and turn it off;
- restrict the images a runner accepts, and know that a missing key allows all;
- drop the Linux capabilities a container does not need;
- prove a hardening by replaying the attack and reading the refusal in the job log.

## Before you start

- the `gitlab-ci` basics: a job, a stage, a runner. You can read a TOML file;
- you edit a file owned by root with `sudo`;
- no paid service and no Premium or Ultimate edition is needed.

`dsoxlab clean` puts the runner back in its starting state (privileged, no image
list), so the next lab finds the runner it expects.

A hardened runner cannot run Docker-in-Docker, which needs `privileged = true`. The
page of the lesson explains the options (a dedicated build runner, or a rootless
builder); this lab does not practise them.
