# Lab: a test matrix

Tests that know only one Python version, and a production running two. Build a
matrix, make it vary something real, and tie the build to all of its
combinations.

Companion lesson:
[Matrices](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-15-matrices/).

```bash
dsoxlab run gl-15-une-matrice-de-tests
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-15/pipeline-craft (branch main).
dsoxlab challenge gl-15-une-matrice-de-tests
dsoxlab check gl-15-une-matrice-de-tests
```

Grading reads the jobs GitLab instantiated and the images they pulled: a matrix
that varies nothing runs the same work several times, and this lab refuses to
validate that.
