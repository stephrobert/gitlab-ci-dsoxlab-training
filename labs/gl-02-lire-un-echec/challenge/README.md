# Challenge: read a failure and fix it

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-02/pipeline-craft` on the VM, on the `main` branch.

Its pipeline is **red**. Three errors were introduced: one in the
`.gitlab-ci.yml`, two in the code. They do not show up at the same time.

## Goal (expected state)

1. GitLab **accepts** the pipeline configuration. Its linter, under
   **Build > Pipeline editor**, confirms it on the chosen branch.
2. Both unused imports are gone from the repository, in `app/main.py` and
   `app/routes/health.py`.
3. The **latest** pipeline on the default branch is **green**.
4. The successful jobs' logs carry the trace of the style check **and** of the
   test suite.

## The method, which is the real subject

- a failed pipeline with **no job at all** is a configuration refusal, not an
  execution error. The message is on the pipeline itself, or in the pipeline
  editor;
- a failing job's log is read **from the end**: the last line gives the exit
  code, and the lines above it the tool's summary;
- a ruff error takes two lines: the rule code with its message, then the
  position as `file:line:column`.

## Validation

```bash
dsoxlab check gl-02-lire-un-echec
```
