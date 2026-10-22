# Scenario

This is the level 4 exam, the level called "Secure". There is no step-by-step
guide, no hint, and the defects are not named.

An auditor arrives on the `pipeline-craft` project and asks four questions:

- **who can change what ships to production, and how?**
- **who can read the deployment secret?**
- **what exactly runs in the pipeline, and has anyone checked it?**
- **can you prove all of this without taking your word for it?**

The pipeline is green and the production deployment works. It would still not
survive the audit: it was built to go fast, and nobody ever asked it to be
vouched for.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine. The audit is not a document: it is a set of settings that the forge
reports, and that anyone with a read token can check through its API, without
any paid licence.

## Mission

Make the pipeline **auditable**: five promises are not kept, and it is up to you
to find them and make them true, while the deployment keeps working.

That is the skill of this level. Securing a chain is not a single tool: it is
the sum of small guarantees that hold together, each of which can be read by
someone who did not build it. Read the project the way an auditor would, from
the API.

## What the exam grades

It grades **the state the forge reports**, never the commands typed:

1. the deployment secret is held as the forge would want a secret held;
2. the default branch can no longer be rewritten by just anyone;
3. a merge request cannot be merged on a red pipeline;
4. what the pipeline's own jobs pull is pinned to an immutable reference;
5. the latest pipeline of the default branch is healthy, it shows scanner
   reports, and the production deployment still went through.

## What the exam does not grade

Not how you obtain a digest, not which scanner template you pick, not the name
of any new setting. Two Premium features are out of scope and not asked:
approval rules and protected environments.
