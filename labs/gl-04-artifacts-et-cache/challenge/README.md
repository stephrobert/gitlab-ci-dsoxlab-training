# Challenge: cache and test report

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-04/pipeline-craft` on the VM, on the `main` branch.

Its pipeline is green, but every job reinstalls its dependencies and the test
results are only readable in the logs.

## Goal (expected state)

1. The **latest** pipeline on the default branch is **green**.
2. The pipeline's **test report** is filled, with no failure. Visible in the
   pipeline's **Tests** tab.
3. A cache was **created**.
4. A cache was **restored** at least once, which needs a **second run** of the
   pipeline.

## What is not imposed

Neither the job names, nor the cache key, nor the cached path. Caching pip's
directory under another path qualifies just as well.

## Validation

```bash
dsoxlab check gl-04-artifacts-et-cache
```
