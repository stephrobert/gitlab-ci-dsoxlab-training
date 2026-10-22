# Lab: turn the scanners on, and read what they say

A green pipeline that only looks at tests, and a secret written in the code that
nobody has ever seen. You turn on SAST and Secret Detection, you read their JSON
reports, and you fix what they point at.

Companion lesson:
[Security scanners](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/fondamentaux/securite-scanners/).

```bash
dsoxlab run gl-21-activer-les-scanners
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-21/pipeline-craft (branch main).
dsoxlab challenge gl-21-activer-les-scanners
dsoxlab check gl-21-activer-les-scanners
```

This lab runs on GitLab **Community Edition**: it only practises the features of
that edition. The Security Dashboard, the project vulnerability reports and the
merge request approval policies are Ultimate features, and are not used here.
Reports are read as files.

The grade comes from the jobs the forge actually ran and the reports they left,
never from the content of `.gitlab-ci.yml`: an included template that never ran
is worth nothing. The runners need internet access to download the scanner
images.
