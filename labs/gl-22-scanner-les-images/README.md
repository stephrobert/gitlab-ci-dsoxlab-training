# Lab: scan the image, and stop shipping a critical flaw

A pipeline that publishes its image without ever looking at it, and an image
that carries a real critical vulnerability. You scan with Trivy, keep the
report, block the pipeline on a critical, and rule out the single finding the
security team triaged, writing why.

Companion lesson:
[Security scanners](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/fondamentaux/securite-scanners/).

```bash
dsoxlab run gl-22-scanner-les-images
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-22/pipeline-craft (branch main).
dsoxlab challenge gl-22-scanner-les-images
dsoxlab check gl-22-scanner-les-images
```

Grading is taken on what the forge saw: a scan job that ran, a Trivy report kept
in its artifacts, a pipeline that really failed because of a critical, and a
justified exception that only covers the triaged finding. A `.gitlab-ci.yml`
that declares a scan job proves nothing.

## What you will be able to do

- scan a published image with Trivy from a GitLab CE pipeline;
- keep a JSON report even when the job fails;
- fail the pipeline on a critical vulnerability, before the deployment;
- rule out a false positive in `.trivyignore`, writing the reason next to it.

This lab needs access to Docker Hub and to Trivy's vulnerability database from
the VM.
