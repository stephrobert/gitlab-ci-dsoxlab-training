# Scenario

The pipeline is red, and nobody understands why.

The pipeline page shows **"failed"** and **no job**. Not a failed job: not a
single job at all. There is no log to open, and the API field meant for
configuration errors answers `null`. The last commit touched the orchestration
added in the previous lab.

And once that first problem is fixed, a second one remains, less visible but
more expensive: this pipeline has **no defences**. No job is bounded in time,
none recovers from a runner failure, and both deployments can start at the same
time on the same environment.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Two steps, and the first one commands the second.

1. **Repair what blocks everything.** As long as GitLab refuses the
   configuration, there is no pipeline, so there is nothing to make reliable.
2. **Make it reliable without hiding anything.** A retry, timeouts, a
   deployment lock.

## Why a pipeline with no job at all

GitLab compiles the whole configuration before creating a single job. One
defect anywhere, and it creates none: the pipeline is born already lost.

The trap is that the pipeline page does not say which one. The API field
reserved for configuration errors stays empty, and the interface settles for
the word "failed". Only one place names the cause: the project's **CI linter**,
which compiles a branch's configuration and returns its errors in plain words.
It is the same reflex as the diagnosis lab: when the pipeline will not talk,
ask whoever compiles it.

## The reliability trap, and it is the whole lab

Retrying a failed job looks like the right answer to everything. It is not, and
this is the one place in this course where a reliability setting makes a
pipeline **less** reliable.

A job fails for two families of reasons that have nothing in common:

- **the runner dies, the API does not answer, the job waits for a free
  runner.** Nothing was wrong. Retrying is exactly the right answer;
- **the script fails.** Something is wrong. Retrying only postpones the
  diagnosis, and a flaky test eventually passes **by chance**. The retry then
  hides precisely what it was meant to report, and the team stops trusting
  green.

A retry is therefore **targeted** at infrastructure reasons. GitLab's keyword
allows it, provided you name the reasons one by one.

## A deployment is not a build

The main file grants every job the right to be cancelled when a new commit
arrives. For a build, that is a saving: cancelled, it leaves nothing behind.

For a deployment, it is a danger. Interrupted halfway, it leaves the
environment in a state nobody described: half the files copied, the service
restarted or not. A deployment is seen through to the end.

The same reasoning applies to two deployments starting together on the same
environment: the last one started is not necessarily the last one finished, and
the environment keeps whichever version finished last. GitLab can serialise two
jobs under a **named lock**: the second waits until the first releases it.

## What the lab checks

1. every deployment carries a **lock**, and the forge really **created** those
   locks: a setting that produces no server-side object has not taken effect;
2. a **retry exists**, and **none of them catches a script failure**;
3. deployments carry a **timeout** and are **no longer cancellable**, both read
   in the configuration as **GitLab compiled it**, inheritance resolved.

## What the lab does not check

Not the name of your locks, not the value of your timeouts, not the exact list
of retry reasons you keep. There is more than one right answer, and it is the
property that counts, not the recipe.
