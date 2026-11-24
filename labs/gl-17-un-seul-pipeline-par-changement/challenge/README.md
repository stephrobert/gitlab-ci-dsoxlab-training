# One change, one pipeline

## The situation

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

## What is asked

### Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-17/pipeline-craft` on the VM, on the `main` branch.

A branch carrying an open merge request starts two pipelines for the same
commit.

### Goal (expected state)

1. An **open merge request** exists, from a branch other than the default one.
2. On the **last commit of that branch**, there is only **one** pipeline, and
   its source is `merge_request_event`.

### The three steps

1. fix the `workflow:`;
2. push a branch and **open the merge request**;
3. push a commit **after** opening it: that is the one being measured.

### Two reminders

- GitLab stops at the **first matching rule**. A refusal rule placed too high
  also closes the merge request;
- the request must be open **before** the measured push, otherwise the variable
  GitLab consults is empty when it evaluates the rules.

### Counting a commit's pipelines

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
SHA=$(git rev-parse HEAD)
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?sha=$SHA" \
  | jq -r '.[] | "\(.id) \(.source) \(.status)"'
```

### Validation

```bash
dsoxlab check gl-17-un-seul-pipeline-par-changement
```
