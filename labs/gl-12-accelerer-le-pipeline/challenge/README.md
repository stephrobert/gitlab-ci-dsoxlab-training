# Make the pipeline faster

## The situation

The `pipeline-craft` pipeline takes seven minutes. Nobody really complains, and
everybody waits.

Two wastes hide in it, and the first one is invisible. The pipeline does have a
cache: it is declared, it is created on every run, it takes disk space. And it
**only ever serves once**.

Its key is `$CI_COMMIT_SHA`. Two jobs of the **same** pipeline share that SHA,
hence the same key: the second one does find the first one's cache, and its log
proudly announces a successful extraction. But on the next commit the SHA
changes: the previous run's cache still exists, under a name nobody will look
for again.

That is what makes the defect so durable. The logs show a cache that works,
because it does work, inside one pipeline. What it never does is cross two
commits.

The second one shows in the pipeline graph: the jobs **queue**. The tests wait
for the lint to finish, when they have no need of it.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Make the pipeline faster by dealing with both causes.

- **the cache key** decides how long it lives. A key that changes on every
  commit makes the cache unfindable; a key derived from the dependency file
  changes only when the dependencies do, which is exactly the right frequency;
- **the order of stages** is a constraint, not a fate. A job can be freed from
  it, and start as soon as the pipeline does.

## What the lab checks

1. the **cache key is the same** from one pipeline to the next. What is
   measured is not the restoration, which already happens at the start, but
   the key's stability;
2. two jobs from **different stages overlapped in time**.

Both are read from what the server produced, not from your file: the keys in
the job logs, the overlap in their timestamps. The API exposes neither declared
keys nor dependencies. Point 1 therefore needs **two runs** to compare.

## A measure that is not one

You are not asked to prove a duration. It varies with the machine's load, and a
pipeline that is faster once proves nothing. What is measured are the two
mechanics that bring the duration down, not the duration itself.

## Two jobs of the same stage do not count

They already run together, without anyone deciding anything. So the lab
compares jobs from **different** stages: that is where the default order
applies, and therefore where a decision shows.

## What is asked

### Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-12/pipeline-craft` on the VM, on the `main` branch.

Its cache is never read back, and its jobs queue.

### Goal (expected state)

1. The **cache key** is the same from one pipeline to the next.
2. Two jobs from **different stages overlapped in time**.

### Two reminders

- the key is compared across **two** runs: run the pipeline again after your
  fix. And beware, a restored cache proves nothing here: with a
  `$CI_COMMIT_SHA` key, two jobs of the same pipeline already share it;
- two jobs of the same stage already run together. The lab compares
  **different** stages.

### Checking the overlap

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/jobs" \
  | jq -r '.[] | "\(.name) [\(.stage)] \(.started_at) -> \(.finished_at)"'
```

### Validation

```bash
dsoxlab check gl-12-accelerer-le-pipeline
```
