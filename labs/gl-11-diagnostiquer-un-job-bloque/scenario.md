# Scenario

A colleague touched `pipeline-craft`'s `.gitlab-ci.yml` before going on leave.
Since then the team pushes and **nothing happens**.

No failure, no warning, no skipped job: the Pipelines tab stays empty. Two
people have already re-pushed, assuming a network problem.

And that is only the first failure. The second waits behind it, and it is of
the same family: it says nothing either.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Get the pipeline running again by diagnosing two failures that produce **no
message**.

Those are the expensive ones, because there is nothing to read. Recognising
them means knowing **what should be there**:

- **an empty Pipelines tab** is not an error, it is an absence. Nothing failed,
  nothing was skipped: nothing was created. The question to ask is "what
  decides that a pipeline is born?". GitLab's linter answers that one: queried
  with `dry_run`, it **evaluates the rules** and returns `valid: false` with
  "The pipeline did not run. Review the workflow:rules configuration" when no
  pipeline would be born;
- **a job stuck pending** never fails. It waits for a runner able to take it,
  and if none is, it waits forever. The question becomes "is this job asking
  for something nobody can provide?".

## What the lab checks

1. a **pipeline exists** on the default branch;
2. **no job is stuck pending**, the linter actually ran, and no job failed.

The second point carries several requirements, and that is not a shortcut: on a
state with no pipeline, "no job failed" is true, so it cannot be a test on its
own.

## A status not to mistake for a failure

A **`manual`** job awaits a human decision: it is a healthy job, and the
pipeline has carried one since an earlier lab. That is not the one that is
stuck.

## Where to look

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft

# The linter EVALUATES the rules: it says whether a pipeline would be born,
# and why not. That is the most direct diagnosis of the first failure.
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/ci/lint?dry_run=true&ref=main" \
  | jq '{valid, errors}'

# Is there a pipeline, and from which source?
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=5" \
  | jq -r '.[] | "\(.id) \(.source) \(.status)"'

# Which tags does the instance runner carry?
curl -s -H "PRIVATE-TOKEN: $JETON" "http://gitlab-1.lab/api/v4/runners/all" \
  | jq -r '.[] | {description, tag_list}'
```
