# Scenario

The repository is there, the application runs, the tests exist, the
`Dockerfile` is ready. There is no pipeline left.

Not a broken pipeline: no pipeline at all. No `.gitlab-ci.yml`, no `ci/`
directory, no generation script. What remains is a **specification**, in
`CAPSTONE-LAB-19.md` at the root of the repository, and a forge that waits.

This is the course's synthesis test. No step-by-step guide: what you learned
lab after lab now has to hold together in a single pipeline.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Rebuild a pipeline that meets the specification. Seven requirements, and they
overlap:

1. **five stages**: lint, test, orchestrate, build, deploy;
2. a **modular CI**: the jobs live in several included files, not in one long
   file;
3. a test **matrix** on Python 3.11 and 3.12, whose results are **reported**
   into GitLab;
4. a **dynamic child pipeline**, generated during the run and triggered from an
   artifact;
5. an image **built and published** to the registry, with explicit
   dependencies;
6. a `workflow:` that handles the merge request, the default branch and tags;
7. **reliable** deployments: exclusivity, timeout, targeted retry.

## What the test grades, and what it does not

It grades **the state the forge shows**: the stages of a pipeline that ran, the
files GitLab really included, the matrix instances, the reported test cases,
the child pipeline that was triggered, the tags pushed to the registry, the
deployment locks that were created.

It grades **no job name**, no number of files, no image version, no timeout
value. There is more than one right answer, and the reference solution is one
of them, not the only one.

A single requirement is not measured directly: the three `workflow:` contexts.
Checking them would mean opening a merge request and pushing a tag, which the
workflows lab already measures. Here, the `workflow:` is judged by what it
produces: a pipeline that is born on the default branch.

## Two traps that each have their own lab

You have met them, and they will come back in this order.

**A refused pipeline does not look like a failed one.** GitLab compiles the
whole configuration before creating a single job: one defect anywhere, and it
creates none. The page shows "failed" with not a single job, and the field
reserved for configuration errors stays empty. Only the project's **CI linter**
names the cause.

**An artifact is not a result.** A `pytest` run that writes its XML file
without declaring it as a report leaves a downloadable file and nothing else:
no test count in the pipeline, and nothing in the merge request.

## One constraint of this environment, to know before you start

This forge's registry answers over **HTTP**, not HTTPS. A Docker client refuses
by default to talk to a plain-text registry, and the build job would fail with
no useful explanation. The memo `REGISTRE-DU-LAB.txt`, left next to your
working copy, gives the exact line to write.

This is not a lab oddity: an internal registry over HTTP demands the same thing
in a company. In production the registry is served over HTTPS and the
constraint disappears.
