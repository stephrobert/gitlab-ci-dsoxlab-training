# Scenario

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
