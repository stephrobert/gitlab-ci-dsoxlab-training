# Scenario

The `pipeline-craft` pipeline is in good shape: split, factored, with its
matrix. And all of its jobs are written in advance, in versioned files.

A request comes in that does not fit that mould: on the default branch, the
team would like one extra check, and only there. You can do that with a rule,
of course. But the next request will be "one job per changed service", and the
number of services is not known when the file is written.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Have the pipeline write part of itself.

A **child pipeline** does not need to exist in the repository: it is
**produced during the run**, by one job, then triggered by another.

Three pieces:

- a job that **writes** a pipeline file and publishes it as an artifact;
- a job that **triggers** it, including that artifact;
- a **strategy**, so the parent waits for its child's result.

## The point that decides everything: the strategy

Without `strategy:`, the trigger job goes green **as soon as the child is
started**, without waiting for its result. The parent is then green whatever
happens downstream, and the child pipeline becomes decorative.

Two strategies make the parent wait, and they are not equivalent:

- **`mirror`** reflects the child's status, whatever it is. That is the one
  GitLab recommends, available since version 18.2;
- **`depend`** also waits, but counts as **successful** a failed child whose
  job carries `allow_failure: true`. It therefore hides exactly what it is
  asked to watch. GitLab's documentation says "not recommended, use mirror
  instead".

This lab's instance runs GitLab 19.5.1: `mirror` is available.

## What the lab checks

1. a **child pipeline ran**, triggered by a job of the parent, and it
   succeeded;
2. the **trigger job carries its child's status**, which proves the parent
   waits and reflects.

The second point accepts `mirror` as well as `depend`: the lab measures the
behaviour, not the keyword. The reference solution uses `mirror`.

## Where to look

A job that triggers a downstream pipeline is not an ordinary job. GitLab calls
it a **bridge** and serves it on a separate endpoint:

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/bridges" \
  | jq -r '.[] | {name, status, child: .downstream_pipeline.status}'
```

Looking for it among the ordinary jobs would find nothing.
