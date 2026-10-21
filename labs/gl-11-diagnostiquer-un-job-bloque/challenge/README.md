# Challenge: two silent failures

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-11/pipeline-craft` on the VM, on the `main` branch.

You push, and no pipeline appears. Behind that failure, a second one waits.

## Goal (expected state)

1. A **pipeline exists** on the default branch.
2. **No job is stuck pending**, the linter ran, no job failed.

## Two reminders

- a **`manual`** job awaits a human decision: it is healthy, it is not the one
  blocking;
- removing a job from the pipeline makes it vanish from the stuck jobs without
  fixing anything. The lab checks that the linter **actually ran**.

## Validation

```bash
dsoxlab check gl-11-diagnostiquer-un-job-bloque
```
