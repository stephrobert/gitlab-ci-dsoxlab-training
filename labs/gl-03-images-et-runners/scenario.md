# Scenario

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
