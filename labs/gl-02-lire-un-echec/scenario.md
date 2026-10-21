# Scenario

A colleague pushed code to `pipeline-craft`, and **the pipeline is red**. Nobody
knows why. The team's reflex is to re-run it "just in case", which fixes
nothing: a pipeline that fails for a real reason fails again the same way.

Three errors were introduced, and they do not show up at the same time. The
first one stops GitLab from creating the pipeline at all: while it is there,
**no job runs**, so nothing else can be reported. The other two are in the
code, and only a failing job's log reveals them.

The project is in the lab forge, with its failed pipeline. A copy of the
repository is waiting for you on the machine.

## Mission

Get the pipeline back to green by reading GitLab's messages instead of
guessing.

Two families of errors await you, and telling them apart is the whole point:

- a **CI configuration** error, which GitLab catches **before** running a
  single job. Its symptom is unmistakable: a failed pipeline with **no job at
  all**;
- **code** errors, which only a failing job reveals, in its log.

At the end, the latest pipeline on the default branch must be **green**, and
both steps, style check and test suite, must have actually run and passed.

## What the lab checks

Grading reads the state left on the forge, and it measures the **three fixes**,
not just the final green:

1. GitLab **accepts** the configuration, as its own linter confirms;
2. both unused imports are gone from the **repository**, not just from your
   machine;
3. the latest pipeline on the default branch is green;
4. the successful jobs' logs carry the trace of the lint **and** of the tests.

That last point closes a tempting shortcut: deleting the lint job turns the
pipeline green without fixing a single line.
