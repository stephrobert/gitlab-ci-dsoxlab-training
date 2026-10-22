# Lab: rebuild the whole pipeline

The course's synthesis test. The repository has no CI file left: a
specification, and everything to rebuild.

Companion lesson:
[Industrial capstone](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-19-capstone-industriel/).

```bash
dsoxlab run gl-19-reconstruire-tout-le-pipeline
# The project is in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-19/pipeline-craft (branch main).
# The specification is in CAPSTONE-LAB-19.md, at the root of the repository.
# This environment's registry constraint is spelled out in
# /opt/dsoxlab/gl-19/REGISTRE-DU-LAB.txt.
dsoxlab challenge gl-19-reconstruire-tout-le-pipeline
dsoxlab check gl-19-reconstruire-tout-le-pipeline
```

Grading is taken on the state the forge shows: five stages carrying jobs, the
files GitLab really included, the matrix instances, the reported test cases,
the triggered child pipeline, the registry tags and the deployment locks. No
job name is imposed.
