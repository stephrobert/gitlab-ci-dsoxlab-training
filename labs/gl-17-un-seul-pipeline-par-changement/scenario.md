# Scenario

Since the team moved to merge requests, the runner queue has doubled. And
nobody added a job.

Every push to a branch carrying an open merge request produces **two pipelines**
for the **same commit**: the branch one, and the merge request one. The same
tests, twice, on the same code. The merge request shows two results, and when
one is green and the other red, nobody knows which counts.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Make one change produce **one** pipeline, and the right one.

Two pipelines overlap, so one has to be closed. Which one?

- **the merge request one** knows the **target** of the merge. It can compare,
  tell what changed against the destination branch, and it is the one shown in
  the merge request;
- **the branch one** knows none of that. It only sees a commit on a branch.

So it is the **branch** pipeline that gets closed, and only when a merge
request is open: on a branch without one, it remains the only one that can run.

## The trap, and it is the whole lab

**GitLab evaluates rules top to bottom and stops at the first match.** A rule
refusing branch pipelines, placed before the one accepting the merge request
event, will **also** close the merge request: a merge request pipeline is also
a pipeline on a branch.

The order is not a matter of style, it is the block's logic.

## What the lab checks

1. an **open merge request** exists, from a branch other than the default one.
   Without it the duplicate cannot happen, so nothing can be measured;
2. on the **last commit of that branch**, there is only **one** pipeline, and
   it comes from the **merge request event**.

## An order to respect in the gestures too

The merge request must be **opened before** the push you want to measure.
Opened afterwards, the variable GitLab consults to know whether a request
exists is empty when it evaluates the rules, and the branch pipeline is born
anyway.
