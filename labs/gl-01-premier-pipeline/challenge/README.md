# Challenge: your first pipeline

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-01/pipeline-craft` on the VM. It has **no
`.gitlab-ci.yml`** and its Pipelines tab is empty.

The repository already carries everything you need: the code under `app/`, a
test suite under `tests/`, the development dependencies in
`requirements-dev.txt` (ruff and pytest included), and a `Dockerfile`. All
three commands pass by hand: `ruff check app/ tests/`, `pytest -v` and
`docker build -t pipeline-craft:test .`.

## Goal (expected state)

1. The repository carries a `.gitlab-ci.yml` on its default branch.
2. The **latest** pipeline on that branch is **green**.
3. That pipeline has **at least three successful jobs**, spread over **more
   than one stage**: a single-job pipeline does not show its steps.
4. Those jobs' logs carry the trace of the **three steps**: style check, test
   suite, image build.

Job names, stage names and the contents of your file do not count: grading
reads the pipeline's state from GitLab's API, not your intentions.

## Validation

```bash
dsoxlab check gl-01-premier-pipeline
```
