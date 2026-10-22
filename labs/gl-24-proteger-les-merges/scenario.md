# Scenario

The `pipeline-craft` pipeline is **green**: a `tester` job, then a
`deployer-production` job that deploys to the `production` environment. Nothing
is broken. That is precisely the problem: the project carries **no lock**.

Today, with the Developer role, anyone can:

- push straight to `main`, or rewrite its history;
- create a `v1.0.0` tag, the thing a release pipeline deploys;
- merge a merge request whose pipeline is red, or whose reviewer's remark is
  still open.

A lock is not a line of `.gitlab-ci.yml`. It is a **setting the forge holds**,
and the forge is the only one that enforces it. The project is in the lab forge.
A copy of the repository waits on the machine, with a note: `NOTE-VERROUS.txt`.

## Mission

Four locks, then one proof.

1. **Protect `main`.** A Developer must no longer be able to push to it, force
   push must be off, and merging must stay possible: a branch nobody can merge
   into is not protected, it is frozen.
2. **Protect the release tags.** Only Maintainers create a tag such as
   `v1.0.0`. A tag is protected through a pattern, which must cover your release
   tags.
3. **Require a successful pipeline before any merge.**
4. **Require every discussion to be resolved before any merge.**
5. **Prove that the locks let a legitimate deployment through.** Run a pipeline
   on `main` and wait for it: `tester` and `deployer-production` must both pass.

The last step is not a formality. Locks that forbid everything are not
protection: they protect production by making it undeployable.

## What the lab checks

1. `main` is protected: nobody below Maintainer pushes to it, force push is off,
   and someone can merge into it;
2. a protected tag pattern covers `v1.0.0`, and only Maintainers create it;
3. the project requires a successful pipeline before merging;
4. the project requires resolved discussions before merging;
5. a pipeline has run on `main` since the start, finished, and both jobs
   `tester` and `deployer-production` succeeded.

The lab reads the **settings** the forge holds, through its API, and what the
pipeline did. It never reads `.gitlab-ci.yml`, and it does not impose the way you
set the locks: interface or API.

## Two limits to know

The forge does not date a lock. The lab cannot prove that your pipeline ran
**after** you set the locks: it proves a pipeline succeeded since the start. Run
it after, that is the point of the proof. And the lab measures the **setting**,
not the refusal it causes: it does not try a forbidden push.

## What a licence adds

Everything above works in GitLab Community Edition. Two more locks come with a
Premium licence and are not practised here: the **approval rule** (a merge
request needs the approval of named people) and the **protected environment**
(only named roles deploy to `production`). On the lab forge, the
`protected_environments` API answers `404 Not Found`.
