# One orchestrator, one file per stage

## The situation

The `pipeline-craft` pipeline is clean. No more duplication, a cache that
serves, jobs that no longer wait for each other: the previous lab did its work.

It is eighty lines long. Six jobs, four stages, a workflow, variables, two
templates. All of it correct, and nobody reads it whole any more: to change the
Python version you scroll to the right block and hope you did not miss one.

And a new team is arriving, who would like to add two security jobs. To that
file.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Split the pipeline, and keep a readable orchestrator.

The question to settle is not "where to cut" but **what stays at the centre**:

- **what is common** stays in `.gitlab-ci.yml`: the list of stages, which says
  the order, and the `workflow:`, which says when a pipeline is born. Spread
  over four files, you would have to open all four to answer those two
  questions;
- **what belongs to a stage** goes with it, into an included file.

## A useful surprise

Included files **do not compartmentalise anything**: GitLab merges them all
before evaluating anything. A hidden job declared in one file is therefore
visible from another, and a job can extend it without importing a thing.

A **YAML anchor**, on the other hand, does not cross files: it is resolved file
by file, before the merge. That is the most useful difference to remember
between the previous lab's two mechanisms.

## What the lab checks

One test, because only one thing really changes:

1. **GitLab reports several included files**. It names them itself: an
   inclusion is not resolved in the YAML, it is made by GitLab;
2. the behaviour **has not moved**: the jobs run, none fails, coverage is
   reported;
3. the orchestrator **keeps** the stages and the workflow.

Points 2 and 3 are guardrails, true from the starting state: they are added to
the first rather than forming tests of their own.

## One difference from the previous lab

In lab 13, grading had to read your file: `extends` and anchors are resolved
before GitLab sees them. Here GitLab **knows** it included files, and its
linter says so. The measure moves back to the server side, where it belongs.

## What is asked

### Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-14/pipeline-craft` on the VM, on the `main` branch.

Its pipeline is eighty lines long, and all of it is correct.

### Goal (expected state)

1. GitLab reports **at least two included files**.
2. The behaviour has not moved: no failed job, at least four successful ones,
   and coverage still reported.
3. The merged configuration still carries `stages:` and `workflow:`.

### Two things to know

- included files **do not compartmentalise**: a hidden job declared in one is
  visible from another, GitLab merging everything before evaluating;
- a **YAML anchor** does not cross files. It must live in the same file as its
  `<<:`.

### Checking what GitLab included

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/ci/lint?dry_run=true&ref=main" \
  | jq '{valid, includes}'
```

A badly written `include:` does not always raise an error: it may simply
include nobody.

### Validation

```bash
dsoxlab check gl-14-externaliser-les-jobs
```
