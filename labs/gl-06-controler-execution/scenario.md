# Scenario

The `pipeline-craft` pipeline works, and it works **too much**. Every push
triggers everything: on a draft branch, on a branch created just to save an
experiment, on a typo fix in the README. Three jobs, every time, with their
package installs and their image build.

And at the other end, nothing is deployed. The pipeline builds an image and
stops there. Getting the code into staging happens by hand, when someone
remembers.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Take back control of **when**.

Three levels of decision, from the broadest to the finest, and confusing them
is the most common mistake:

- **is a pipeline born?** That is the `workflow:` block's question. Without it,
  a pipeline starts on every push, on every branch;
- **does this job join the pipeline that was born?** That is the question of
  the `rules:` set on the job;
- **does this job start on its own?** A job can join the pipeline and wait for
  a human to trigger it.

Also add two deployments: **staging**, which goes on its own when the default
branch moves, and **production**, which waits for a decision.

## What the lab checks

1. a deployment job **succeeded** automatically on the default branch;
2. another deployment job waits for a **human decision**, in `manual` status;
3. **no job failed**: adding two jobs does not break what worked. Mind the
   pipeline's own status, which becomes **`manual`** rather than "success"
   while the production deployment awaits its decision: that is the intended
   state, not a failure;
4. the configuration carries a `workflow:` block.

One honest note on point 4: a `workflow:` block's effect can only be observed
by pushing to a branch that must trigger nothing, which a test has no business
doing. So the lab reads the configuration **as GitLab understood it**, the one
its linter returns, not your file.

## One quirk of the lab forge

This GitLab's registry runs over **HTTP**. The build job's Docker service is
told so by an option, set for you in the starting state. On gitlab.com, over
HTTPS, the question does not arise.
