# Challenge: a child pipeline

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-16/pipeline-craft` on the VM, on the `main` branch.

All of its jobs are written in advance.

## Goal (expected state)

1. A **child pipeline ran** and succeeded, triggered by a job of the parent.
2. The **trigger job carries its child's status**, and no job of the parent
   failed.

## The three pieces

- a job that writes a pipeline file and publishes it as an **artifact**;
- a job that triggers it, with `trigger: include: - artifact: … job: …`;
- a **strategy**: `mirror` preferably, `depend` accepted.

## Two reminders

- without `strategy:`, the parent goes green as soon as the child is
  **started**;
- a trigger job is read on `/pipelines/:id/bridges`, not in the job list.

## Validation

```bash
dsoxlab check gl-16-un-pipeline-enfant
```
