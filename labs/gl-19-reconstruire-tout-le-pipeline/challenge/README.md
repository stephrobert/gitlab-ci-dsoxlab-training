# Rebuild the whole pipeline

## The situation

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

## What is asked

### Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-19/pipeline-craft` on the VM, on branch `main`.

The repository has **no CI file at all**. The specification is in
`CAPSTONE-LAB-19.md`, at the root of the repository.

### Goal (expected state)

1. a pipeline runs on the default branch, **with no failed job**, and its
   **five stages** carry jobs: lint, test, orchestrate, build, deploy;
2. GitLab **included at least two local files**: the CI is modular;
3. the **matrix** produces at least two instances, one on Python 3.11 and one
   on 3.12, and the pipeline's **test report** is not empty;
4. a **child pipeline** was triggered from an artifact, and it did not end in
   failure;
5. the project's **registry** holds at least one tag;
6. the forge holds at least one **deployment lock**, deployments carry a
   **timeout**, and **no retry** covers a script failure.

### Before you start: this environment's registry

It answers over HTTP. The memo `/opt/dsoxlab/gl-19/REGISTRE-DU-LAB.txt` gives
the line to write so the job's Docker service agrees to talk to it.

### The four commands that help you check

Ask GitLab what it understood of your configuration, and what it included:

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/ci/lint?dry_run=true&ref=main" \
  | jq -r '.valid, .errors[]?, (.includes[]?.location)'
```

Read the last pipeline's test report, which stays empty if the JUnit report is
not declared as one:

```bash
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/test_report" \
  | jq '{total_count, failed_count}'
```

Find the child pipeline, which GitLab does **not** serve among the jobs:

```bash
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/bridges" \
  | jq -r '.[] | "\(.name) \(.status) child=\(.downstream_pipeline.status // "none")"'
```

Count the deployment locks and the published tags:

```bash
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/resource_groups" | jq -r '.[].key'
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/registry/repositories" | jq -r '.[].id'
```

### Validation

```bash
dsoxlab check gl-19-reconstruire-tout-le-pipeline
```
