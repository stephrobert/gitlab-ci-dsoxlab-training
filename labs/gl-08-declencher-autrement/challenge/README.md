# Challenge: start a pipeline without a push

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-08/pipeline-craft` on the VM, on the `main` branch.

Its pipeline can only be born from a push, and the project has neither a
schedule nor a trigger token.

## Goal (expected state)

1. A **schedule** exists and is **active**.
2. A **trigger token** exists.
3. A pipeline ran from a source **other than a push**, with no failed job.
4. One job appears **only** in that pipeline, not in a push one.

## Two leads

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

## Validation

```bash
dsoxlab check gl-08-declencher-autrement
```
