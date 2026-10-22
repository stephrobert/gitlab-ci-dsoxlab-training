# Exam: a pipeline to industrialise

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-ep4/pipeline-craft` on the VM, on branch `main`.

The pipeline is green, but it is only half industrialised. Several things that
a team would require before reusing it are missing. It is up to you to find
which, and to fix them without ever leaving `main` red.

## Goal (expected state)

1. shared parts are written once (include or `extends`);
2. jobs are linked as a graph and start without waiting for their whole stage;
3. the tests run as a matrix, each instance with a non-empty test report;
4. a child pipeline built from a job artifact runs and succeeds;
5. the deployment is locked and has a time limit, retries only cover system
   failures, and a transient failure is absorbed;
6. the latest pipeline of `main` is green and comes from your changes.

## No hints are provided

This is an exam: the defects are not named, and there is no hint to unlock. You
have seen every gesture in the labs of this level. Everything you need to read
is in the repository copy and the forge API; the VM holds a token for it (see
the note next to the repository copy).

## Validation

```bash
dsoxlab check gl-ep4-un-pipeline-a-industrialiser
```
