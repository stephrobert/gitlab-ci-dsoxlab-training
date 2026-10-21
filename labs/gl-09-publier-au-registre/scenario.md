# Scenario

The `pipeline-craft` pipeline builds a Docker image on every run on the default
branch. Then the job ends, and the image goes with it.

Nobody can deploy it: it would have to be rebuilt, hoping to get the same one.
And when staging breaks, nobody can say which version is running, because no
image has a lasting name.

The lab forge has a **container registry**, and it is empty.

The project is in the forge. A copy of the repository is waiting for you on the
machine.

## Mission

Publish the image from the pipeline, under a name that designates the code it
contains.

Two ideas, and the second is the one that matters:

- **publishing** means authenticating, then pushing. GitLab hands the job
  everything it needs: the registry address, a disposable username and
  password, and the project's full image path. Three `CI_REGISTRY_*` variables
  to know;
- **staying traceable** means naming the image after the **commit**. A tag that
  designates one precise commit lets you say, six months later, which code runs
  in production. A moving tag does not.

## One quirk of the lab forge

This GitLab's registry listens over **HTTP**. The job's Docker service is told
so by an option, set for you in the starting state. On gitlab.com, over HTTPS,
the question does not arise.

## What the lab checks

1. the project registry holds **at least one image**;
2. a published tag carries the **short SHA of the default branch's last
   commit**;
3. a successful job's log shows that **the pipeline** published it, not a hand
   on a keyboard;
4. no job in the pipeline failed.

Point 2 is the heart of the lab. A prefix or suffix around the SHA is fine:
`sha-1a2b3c4d` qualifies as much as `1a2b3c4d`. What is refused is that no tag
designates the commit.

## About the `latest` tag

You may publish one, the lab accepts it. It does not require one, and that is
not an oversight: a moving tag invites whoever consumes the image to take a
reference that shifts under their feet. The commit tag always says the same
thing.
