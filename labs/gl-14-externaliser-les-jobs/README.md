# Lab: one orchestrator, one file per stage

A correct, eighty-line pipeline that nobody reads whole any more. Move the jobs
into included files, and keep at the centre what says the order and the
trigger.

Companion lesson:
[Templates and include](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-14-templates-include/).

```bash
dsoxlab run gl-14-externaliser-les-jobs
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-14/pipeline-craft (branch main).
dsoxlab challenge gl-14-externaliser-les-jobs
dsoxlab check gl-14-externaliser-les-jobs
```

Grading moves back to the server side: GitLab names the files it included
itself, where the previous lab's factorisation left no trace at all.
