# Challenge: factor the pipeline

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-13/pipeline-craft` on the VM, on the `main` branch.

Its pipeline works and repeats itself.

## Goal (expected state)

1. The file carries a **hidden job** extended by at least one job, and a **YAML
   anchor** merged with `<<:`.
2. The behaviour **has not changed**: no failed job, at least four successful
   ones, and coverage still reported.

## What is not imposed

Neither the hidden job's name, nor the anchor's, nor how many of each. Two
hidden jobs and three anchors qualify as much as one of each.

## Two reminders

- `extends:` merges **deeply**: a job can inherit a cache and redeclare only
  its policy;
- `coverage:` belongs to the **job**. Losing it while moving the test job
  leaves the pipeline green and the coverage empty.

## Validation

```bash
dsoxlab check gl-13-factoriser-le-yaml
```
