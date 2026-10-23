# Scenario

This is the level 3 exam, the level called "Industrialise". There is no
step-by-step guide, no hint, and the defects are not named.

The `pipeline-craft` project has a pipeline that is green. A colleague wrote it
quickly, it works, and the team now wants to run it for ten more projects. Your
tech lead asks four questions:

- **is it written once, or copied?**
- **how long does a change wait, and for what?**
- **what happens when a step fails for a reason that is not the code?**
- **what stops two deployments from running at the same time?**

A copy of the repository is waiting for you on the machine, and the project is
in the lab forge. The jobs only run small shell scripts from `qa/`: the exam
grades the pipeline structure, not an application.

## Mission

Industrialise the pipeline without breaking it: every change must leave the
latest pipeline of `main` green. Read the existing pipeline the way a reviewer
would, find what is not industrial about it, and fix it.

This differs from the lab that precedes it. There you built from a
specification. Here you diagnose an existing pipeline, and nobody tells you
where to look.

## What the exam grades

It grades **the state the forge reports**, never the commands typed:

1. the shared parts are written once (include or `extends`);
2. the jobs form a graph, and a job starts before its whole stage is over;
3. the tests run as a matrix, and each instance reports a non-empty test report;
4. a child pipeline built from a job artifact runs and succeeds;
5. deployment is locked and bounded, retries are limited to system failures
   and a transient failure is absorbed;
6. the latest pipeline of `main` is green and is the result of your work.

## What the exam does not grade

Not the names you give your files or jobs, not how many files you split the
configuration into. Cross-project triggers are out of scope.
