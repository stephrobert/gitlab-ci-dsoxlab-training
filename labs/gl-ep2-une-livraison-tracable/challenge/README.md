# Exam: a delivery you can trace

## The situation

This is the level 2 exam, the level called "Deliver". There is no step-by-step
guide, no hint, and the defects are not named.

This project's chain builds, tests and deploys. It leaves no trace at all.

Nobody can answer these questions, and yet they come up every week:

- **what is running in production, and since when?**
- **which image was that deployment based on?**
- **who decided to ship?**

And a fourth problem stops you from answering the first three: the pipeline
never finishes.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Make the delivery **traceable**: four traces are missing, and it is up to you
to find them and make them exist.

That is the skill of this level, and it is widely misunderstood. Delivering is
not copying files onto a server: it is being able to say, six months later,
which version runs where, where it came from, and who decided it. A deployment
you cannot trace did not happen, from the point of view of the team that will
have to pick it up.

## One defect blocks the others, start there

A job can fail to start **without failing**. There is then no message, no log,
and the pipeline stays in progress indefinitely: everything after it never
happens.

It is the most unpleasant failure in GitLab CI, because it produces nothing to
read. You diagnosed it in one of this level's labs: the reflex is to compare
what the job **asks for** with what the project's runners **offer**.

## What the exam grades

It grades **the state left in the forge**, never the commands typed:

1. no job of the last pipeline is waiting, and none failed;
2. the project holds at least one **environment**, and at least one
   **successful deployment** is recorded there;
3. the project's **registry** holds at least one tag;
4. no production job started on its own on the default branch.

## What the exam does not grade

Not the name of your environments, not their URL, not how you protect
production. On that last point two answers work and both are accepted: the job
waits for a human, or it only runs on a deliberately pushed tag.

## What is asked

### Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-ep2/pipeline-craft` on the VM, on branch `main`.

The chain builds, tests and deploys without leaving a trace. Four traces are
missing, and one of them blocks the others.

### Goal (expected state)

1. no job of the last pipeline on `main` is waiting, and none failed;
2. the project holds at least one **environment**, and at least one
   **successful deployment** is recorded there;
3. the project's **registry** holds at least one tag;
4. no production job started on its own on the default branch.

### No hints are provided

This is an exam: the four defects are not named, and there is no hint to
unlock. You have seen all of it in the four labs of this level.

### One constraint of this environment

This forge's registry answers over **HTTP**, not HTTPS. A Docker client
refuses by default to talk to a plain-text registry: the job's Docker service
has to declare the registry address as insecure. The starting pipeline already
does this; it is a given, not a defect.

### The commands that help you check

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft

# The real state of the last pipeline's jobs
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/jobs" \
  | jq -r '.[] | "\(.name) \(.status)"'

# What the project's runners offer, to compare with what the jobs ask for
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/runners" \
  | jq -r '.[] | "\(.description) \(.tag_list // [])"'

# The environments and the recorded deployments
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/environments" | jq -r '.[] | "\(.name) \(.state)"'
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/deployments" \
  | jq -r '.[] | "\(.environment.name) \(.status) \(.ref)"'

# The published images
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/registry/repositories" | jq -r '.[].id'
```

### Validation

```bash
dsoxlab check gl-ep2-une-livraison-tracable
```
