# Lab: protect what merges, and what deploys

A green pipeline deploys to production from a project with no lock at all. You
protect the `main` branch, the release tags,
you require a successful pipeline and resolved discussions before any merge, and
you prove the locks still let a legitimate deployment through.

Companion lesson:
[GitLab CI: protected branches and tags](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/securite/branches-protegees/).

```bash
dsoxlab run gl-24-proteger-les-merges
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-24/pipeline-craft (main branch).
dsoxlab challenge gl-24-proteger-les-merges
dsoxlab check gl-24-proteger-les-merges
```

The grade is taken on the settings the forge holds, read from its API: a
protected branch, a protected tag pattern, and two merge
conditions. A `.gitlab-ci.yml` proves none of them.

## What you will be able to do

- protect a branch, and say who may push and who may merge;
- protect release tags;
- require a successful pipeline and resolved discussions before a merge;
- check that a lock protects without blocking the legitimate deployment.

This lab needs no paid service and no Premium or Ultimate GitLab edition. The
approval rule and the protected environment, which do need a licence, is named in the scenario and not
practised.
