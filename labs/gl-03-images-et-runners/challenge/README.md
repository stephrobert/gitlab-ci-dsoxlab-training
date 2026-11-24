# The right image for each job

## The situation

The `pipeline-craft` pipeline runs, but it runs badly. All three jobs share the
same image, `python:3.12`, the full Python image: close to a gigabyte pulled
for every job, when running ruff needs a fraction of that.

Worse, the job that builds the Docker image **fails every time**. Nobody on the
team can see why: the command is the right one, and it works on the developers'
machines.

The project is in the lab forge, with its failed pipeline. A copy of the
repository is waiting for you on the machine.

## Mission

Give each job the image that matches its work, and make the image build
succeed.

Two ideas to hold together:

- **a job runs inside the image you give it**, and has only what that image
  contains. A Python image runs Python, not Docker;
- **building an image needs a daemon**, on top of the client. In a pipeline
  that daemon does not come from the runner's machine: it is declared.

For the Python jobs, the full image does the job, but a lighter variant does it
too, for a fraction of the download.

## What the lab checks

Grading reads the **job logs**, where GitLab Runner records the image it
pulled:

1. the latest pipeline on the default branch is **green**;
2. a successful job carries a **completed** `docker build`;
3. a **Docker service** was started for that job;
4. no job pulls the full `python:3.12` image any more.

Point 4 does not dictate the replacement: `-slim`, `-alpine` or another light
base all qualify. What is measured is that the choice was made.

## What is asked

### Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-03/pipeline-craft` on the VM, on the `main` branch.

Its pipeline has three jobs, all on `python:3.12`, and the one that builds the
Docker image fails.

### Goal (expected state)

1. The **latest** pipeline on the default branch is **green**.
2. A successful job carries a **completed** `docker build`.
3. A **Docker service** was started for that job.
4. No job pulls the full `python:3.12` image any more.

### What is not imposed

Neither the job names nor the replacement image for the Python jobs: a `-slim`
or `-alpine` variant, or any other light base, all qualify. Point 4 measures
that the choice was made, not which one.

### Validation

```bash
dsoxlab check gl-03-images-et-runners
```
