# Challenge: make the pipeline faster

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-12/pipeline-craft` on the VM, on the `main` branch.

Its cache is never read back, and its jobs queue.

## Goal (expected state)

1. The **cache key** is the same from one pipeline to the next.
2. Two jobs from **different stages overlapped in time**.

## Two reminders

- the key is compared across **two** runs: run the pipeline again after your
  fix. And beware, a restored cache proves nothing here: with a
  `$CI_COMMIT_SHA` key, two jobs of the same pipeline already share it;
- two jobs of the same stage already run together. The lab compares
  **different** stages.

## Checking the overlap

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/jobs" \
  | jq -r '.[] | "\(.name) [\(.stage)] \(.started_at) -> \(.finished_at)"'
```

## Validation

```bash
dsoxlab check gl-12-accelerer-le-pipeline
```
