# Challenge: a test matrix

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-15/pipeline-craft` on the VM, on the `main` branch.

Its tests only know one Python version.

## Goal (expected state)

1. The matrix produced **at least three** distinct jobs, all successful.
2. Those jobs pulled **different images**, no job failed, and coverage is still
   reported.

## What the repository provides

`tests/` holds three files: `test_health.py`, `test_version.py` and
`test_items.py`. Enough to split a "core" suite and an "api" one.

## Two reminders

- a `needs:` naming a matrix job waits for **all** its instances;
- the reported coverage **drops** when the suites are split: GitLab averages
  the instances. That is not a regression.

## Validation

```bash
dsoxlab check gl-15-une-matrice-de-tests
```
