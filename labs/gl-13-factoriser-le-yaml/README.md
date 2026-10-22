# Lab: factor the pipeline

Two jobs declaring the same image and the same cache, word for word. Factor
them with a hidden job and an anchor, without changing the behaviour.

Companion lesson:
[extends and anchors](https://www.stephane-robert.info/docs/pipeline-cicd/gitlab/labs/lab-13-extends-anchors/).

```bash
dsoxlab run gl-13-factoriser-le-yaml
# The project lives in the lab forge: http://gitlab-1.lab/root/pipeline-craft
# A copy of the repository waits in /opt/dsoxlab/gl-13/pipeline-craft (branch main).
dsoxlab challenge gl-13-factoriser-le-yaml
dsoxlab check gl-13-factoriser-le-yaml
```

This is the only lab in the series whose grading reads the file, and that is
deliberate: `extends` and anchors are resolved before execution, so the
factorisation leaves no trace in the state. The second test checks that the
behaviour has not moved.
