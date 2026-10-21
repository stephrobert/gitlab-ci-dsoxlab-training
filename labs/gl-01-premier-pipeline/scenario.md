# Scenario

You have just been handed `pipeline-craft`, a small FastAPI service that three
people push to every day. It has tests under `tests/`, a linter configured in
`pyproject.toml` and a `Dockerfile`, and they all work:
`ruff check app/ tests/`, `pytest -v` and `docker build .` pass on your
machine.

Nothing runs them on the server. The project has **no `.gitlab-ci.yml` at all**,
so GitLab has never built anything, never run a test, and the Pipelines tab is
empty. Twice last month a change that broke the test suite reached the default
branch, and nobody noticed until a colleague pulled it.

A GitLab instance is waiting for you on `gitlab-1.lab`, with one runner already
registered and able to take untagged jobs. The repository is there, on its
`main` branch.

## Mission

Make the server run what your machine already runs, and prove it.

At the end, the project's latest pipeline on the default branch must be
**green**, and it must have actually done three things: checked the code style,
run the test suite, and built the image. Not a pipeline that merely exists, and
not a pipeline that is green because it does nothing.

How you organise it is up to you. The lab does not care which commands you put
in which job, nor what you name things. It checks three things, read from
GitLab's API: that the latest pipeline on the default branch is green, that it
has at least three successful jobs spread over more than one stage, and that
those jobs' logs carry the trace of the three expected steps.

You will know you are done when the Pipelines tab shows a green run whose jobs
cover the three steps.
