# Start a pipeline without a push

## The situation

The `pipeline-craft` pipeline works well, and it can do exactly one thing:
react to a push. Two of the team's needs run into that.

The first is a **full regression suite** that takes fifteen minutes. Running it
on every push is expensive and pointless: nobody waits for its result. It
belongs to the night, when the machine is free.

The second comes from outside. The team that publishes the image catalogue
would like to **re-run the pipeline** when their own chain finishes. They have
no account on the forge, and want none.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Make the pipeline born from something other than a push, and reserve one job to
a single origin.

First thing to understand: **`$CI_PIPELINE_SOURCE` says where the pipeline
comes from**, and the `workflow:` block decides which origins are accepted. A
source missing from that list produces **no** pipeline at all, and nothing says
so: the tab is simply empty.

Three steps:

- make the `workflow:` accept the `schedule`, `trigger` and `api` sources;
- create an active **schedule** in the forge, and a **trigger token** for the
  neighbouring team;
- reserve the regression suite to the `schedule` source.

## A vocabulary trap

`$CI_MERGE_REQUEST_IID` and `$CI_PIPELINE_SOURCE == "merge_request_event"` look
alike and do not say the same thing: the first also exists in a branch pipeline
attached to a merge request. The second names the origin.

## What the lab checks

1. a **schedule** exists and is **active**;
2. a **trigger token** exists;
3. a pipeline actually ran from a source **other than a push**, and none of its
   jobs failed;
4. one job appears **only** in the non-push pipeline, not in the push one.

Point 4 therefore needs both: a pipeline from elsewhere, and a push pipeline to
compare with. A job's rules are not exposed by the API: comparing them is the
only way to prove a source rule works.

**And a schedule is not waited for, it is played.** The play button under
`Build > Pipeline schedules`, or `POST /pipeline_schedules/:id/play`, starts a
pipeline right away that does carry the `schedule` source. Without it you would
have to wait for the appointed hour to find out whether the rule works. A
schedule you have never played is a schedule you have not checked.

Your tests will never read a trigger token's **value**, only its existence: a
failure message carrying it would publish it.

## What is asked

### Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-08/pipeline-craft` on the VM, on the `main` branch.

Its pipeline can only be born from a push, and the project has neither a
schedule nor a trigger token.

### Goal (expected state)

1. A **schedule** exists and is **active**.
2. A **trigger token** exists.
3. A pipeline ran from a source **other than a push**, with no failed job.
4. One job appears **only** in that pipeline, not in a push one.

### Two leads

Triggering with the token, from the VM:

```bash
curl -X POST --form token=YOUR_TOKEN --form ref=main \
  http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/trigger/pipeline
```

The schedule is created in the UI (`Build > Pipeline schedules`) or through the
API. Its time does not matter for grading: what counts is that it exists and is
active.

To play it right away, without waiting for its hour:

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -X POST -H "PRIVATE-TOKEN: $JETON" \
  http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/pipeline_schedules/1/play
```

The pipeline it starts carries the `schedule` source, the one a job can depend
on.

### Validation

```bash
dsoxlab check gl-08-declencher-autrement
```
