# Scenario

The `pipeline-craft` pipeline tests, and it says so clearly: the pipeline's
Tests tab lists every test, green or red. That is an earlier lab's achievement,
and it holds.

What it does not say is **how much code those tests go through**. In review the
question comes back every time: "is the part you changed tested?", and nobody
can answer without running the suite by hand on their own machine.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Get the coverage all the way to GitLab, and make it useful.

Two steps, and the difference between them is the whole point of the lab:

- **the percentage.** GitLab does not compute coverage: it **reads** it. The
  job must print it in its log, and a regular expression declared on the job
  fishes it out. The figure then shows on the pipeline, on the job, and in the
  merge request;
- **the report.** A percentage says where you stand; a report says what to do.
  Declared as a coverage report artifact, it shows the **uncovered** lines
  right in a merge request's diff.

Without the second, you know you cover 78 % and have no idea which of the 22 %
you are missing.

## What the lab checks

1. a non-zero **coverage** reached GitLab, on the pipeline or on a job;
2. a **coverage report** is published as an artifact, and the earlier work
   holds: the test report is still filled, no job failed.

The second point carries the no-regression requirement, and that is not a
shortcut: the test report and the pipeline's health are true **from the
starting state**, so separate tests would pass before any work.

## A trap that says nothing

A regular expression that matches nothing **produces no error**. The pipeline
stays green, the job succeeds, and the coverage field stays empty. Check the
figure afterwards, on the pipeline page or through the API: that is the only way
to know the fishing worked.
