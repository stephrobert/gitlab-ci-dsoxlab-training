# Scenario

The `pipeline-craft` pipeline is split, factored, fast. It tests on **one**
Python version, 3.12, the one on the machine of whoever wrote the job.

Production runs two: 3.11 on the old servers, 3.12 on the new ones. Nobody
knows whether the code still works on the first, and nobody will until the next
outage.

Besides, the full suite takes time and is run as one block: a failing API test
hides the results of everything else.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Test several combinations at once, and tie the build to all of them.

- **a matrix instantiates the job**, once per combination. Two Python versions
  by two test suites give four jobs, which GitLab names
  `pytest-matrix: [3.12-slim, core]` and so on, and runs in parallel;
- **the build waits for every combination**. Naming the test job in the build's
  `needs:` is enough: GitLab waits for each of its instances. Building an image
  only makes sense if every combination passes.

## A matrix's trap

A matrix can declare four combinations and run **exactly the same work four
times**. The pipeline becomes four times more expensive and learns nothing
more. So what the lab checks is that the combinations **change something**: the
jobs must have pulled different images.

## What the lab checks

1. the matrix produced **at least three** distinct jobs, and they succeeded;
2. the jobs pulled **different images**, which their logs record, and the
   earlier work holds: no failed job, coverage still reported.

## A coverage drop that is not a regression

Each instance only tests part of the code, so each reports partial coverage,
and GitLab shows the **average**. The figure goes down by construction, without
any test having disappeared. That is the price of a matrix that splits the
suites, and it is better known than discovered.
