# Challenge: the right image for each job

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-03/pipeline-craft` on the VM, on the `main` branch.

Its pipeline has three jobs, all on `python:3.12`, and the one that builds the
Docker image fails.

## Goal (expected state)

1. The **latest** pipeline on the default branch is **green**.
2. A successful job carries a **completed** `docker build`.
3. A **Docker service** was started for that job.
4. No job pulls the full `python:3.12` image any more.

## What is not imposed

Neither the job names nor the replacement image for the Python jobs: a `-slim`
or `-alpine` variant, or any other light base, all qualify. Point 4 measures
that the choice was made, not which one.

## Validation

```bash
dsoxlab check gl-03-images-et-runners
```
