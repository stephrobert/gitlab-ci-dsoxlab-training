# Scenario

The `pipeline-craft` pipeline is **green**, and it stays green. Nothing to fix
this time: there is waste to remove and a result to make usable.

Two things the team notices every day:

- **every job downloads its dependencies from scratch**. Three jobs, three
  identical Python package installs, on every run;
- **the test results vanish** with the job. When a test breaks, someone has to
  open the log and read it by hand: the pipeline's Tests tab is empty, because
  nothing fills it.

The project is in the lab forge, with its green pipeline. A copy of the
repository is waiting for you on the machine.

## Mission

Remove the waste and make the results readable.

Two mechanisms, often confused, and telling them apart is this lab's lesson:

- the **cache** carries, from one run to the next, whatever would be expensive
  to rebuild. It is **optimistic**: if it is missing, the job still works, just
  more slowly. Its key decides how long it lives;
- the **artifact** carries a result: to a later job, to a human who downloads
  it, or to GitLab itself when it is a report.

## What the lab checks

1. the latest pipeline on the default branch is **green**;
2. the pipeline's **test report** is filled, with no failure. An artifact
   declared by its path alone is downloadable but never read: it must be
   declared as a report;
3. a cache was **created**;
4. a cache was **restored** at least once.

Point 4 needs **two runs**: a cache is created on the first one and only
restored on the next. It is also the chance to compare the durations.
