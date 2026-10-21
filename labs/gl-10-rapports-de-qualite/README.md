# Lab: make the pipeline say what it covers

Tests that pass and say nothing about how much code they go through. Print the
coverage, have GitLab fish it out, and publish the report that shows the
missing lines.

Companion lesson:
[Quality reports](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-10-rapports-qualite/).

```bash
dsoxlab run gl-10-rapports-de-qualite
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-10/pipeline-craft (branch main).
dsoxlab challenge gl-10-rapports-de-qualite
dsoxlab check gl-10-rapports-de-qualite
```

Grading reads what reached GitLab: the coverage figure and the type of the
published artifacts. A percentage says where you stand; a report says what to
do.
