# Scenario

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
