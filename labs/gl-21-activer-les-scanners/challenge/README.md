# Turn the scanners on, and read what they say

## The situation

The project pipeline is green, and that is what worries people.

It runs the application tests, and nothing else. Nobody has ever looked at what
the code contains from a security point of view, or at what the repository
history has left lying around. An audit is coming, and the question is simple:
**what would a scanner say about this repository today?**

There is an answer, and it is in the code. Someone once wrote a secret where it
should not be, and the application kept working: a defect that breaks nothing
cannot be seen by reading, which is exactly what makes this kind of flaw
dangerous.

The project is in the lab forge. A copy of the repository waits for you on the
machine.

## Mission

1. **Turn on two security scanners** in the pipeline: static analysis of the code
   (**SAST**) and secret detection (**Secret Detection**).
2. **Read their reports.** They are JSON files left by the jobs, and nothing
   else: the lab instance is a GitLab **Community Edition**, which has neither a
   security dashboard nor a vulnerability report in its interface. Those
   features belong to the Ultimate edition; here, the report is a file, and
   reading it is part of the job.
3. **Fix the defect the scanner points at**, then let a new scan confirm it is
   gone.
4. **Write down what the report said** in a `LECTURE.md` file at the root of the
   repository: the file and the line.

## What the scanners return, and what they do not

A GitLab scanner is a **job** like any other. It joins the pipeline through a
template, runs in an image the runner downloads, and leaves its result as an
**artifact**. The `semgrep-sast` (SAST) and `secret_detection` (Secret
Detection) jobs each leave one file, `gl-sast-report.json` and
`gl-secret-detection-report.json`.

The file is a JSON document whose substance is one list, `vulnerabilities`. Each
entry says **where** (`location.file`, `location.start_line`), **what** (the name
and identifier of the rule) and **how bad** (`severity`). An **empty** list is a
result: the scan ran and found nothing. A job that never ran says nothing at
all, and the lab tests make that difference.

A secret scanner is a detective, not a safe. It reports a secret that is
**already committed**; it does not remove it from the history, and nothing else
will: a token that has been pushed is a **compromised** token, which you
**revoke** and replace.

## A reading trap: what the Secret Detection scan looks at

A pipeline started by a push examines the commits that push brings. If the
secret was committed **before** the commit that turns the scanner on, that first
scan may not see it. This is the situation of a team that enables detection on
an old repository, and the remedy is a one-off action: a pipeline started by
hand to re-read the **whole history**. That scan is a **single** operation. Left
in the configuration, it would lengthen every pipeline, and it would find
forever a token nobody can erase from the past.

## What the lab checks

1. **SAST ran**: a successful job left a readable report of type `sast`.
2. **Secret Detection ran**: a successful job left a readable report of type
   `secret_detection`.
3. **A scan saw the defect**: a report, whichever pipeline produced it, points at
   the token written in the code. Erasing the line without having run the
   scanner is therefore not enough.
4. **The defect is fixed and a new scan confirms it**: the file still exists and
   no longer contains the token, and the pipeline of the last commit of `main`,
   started by a push, has a secrets report that no longer points at it. No job
   of that pipeline failed, and the application test still passes.
5. **The reading is written down**: `LECTURE.md` names the file and the line the
   report pointed at.

## What the lab does not check

Neither the names of your jobs, nor the way you store the secret, nor the number
of vulnerabilities in the SAST report. The lab also cannot know whether you
**revoked** the token: that happens in the service that issued it, and nobody but
you can see it. Here the token is made up and opens nothing, but the reflex is
what counts.

## What is asked

### Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits in
`/opt/dsoxlab/gl-21/pipeline-craft` on the VM, on branch `main`.

The pipeline runs the tests and nothing else. Turn on SAST and Secret Detection,
read the reports, fix the defect they point at.

### Goal (expected state)

1. A **SAST** job succeeded and left its report.
2. A **Secret Detection** job succeeded and left its report.
3. A Secret Detection report **points at the token** written in the code.
4. The token is **no longer in the code**, and the pipeline of the last commit of
   `main`, started by a push, confirms it.
5. `LECTURE.md`, at the root of `main`, names **the file and the line** from the
   report.

### The three steps

1. add both templates and wait for the pipeline;
2. read the reports, including the one from a history scan;
3. fix, push, and let the push pipeline confirm.

### The lab runs on a Community edition

There is no Security Dashboard or vulnerability report in the interface: those
are Ultimate features. The report is the job's JSON file. Two ways to read it.

From the job page, the **Browse** button opens its artifacts, where
`gl-secret-detection-report.json` sits. From the VM:

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/jobs?per_page=20" \
  | jq -r '.[] | "\(.id) \(.name) \(.status)"'
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/jobs/<ID>/artifacts/gl-secret-detection-report.json" \
  | jq '.vulnerabilities[] | {file: .location.file, line: .location.start_line, rule: .name}'
```

If the file path answers 404, download the whole archive and open it:

```bash
curl -s -H "PRIVATE-TOKEN: $JETON" -o artefacts.zip "$API/jobs/<ID>/artifacts"
python3 -m zipfile -e artefacts.zip rapport && ls rapport
```

### If the scan does not see the token

A push scan examines the commits it receives, and the token is older. A pipeline
started by hand re-reads the history: **Build > Pipelines > New pipeline**,
branch `main`, variable `SECRET_DETECTION_HISTORIC_SCAN` set to `true`. It is a
**one-off** operation, never to be left in `.gitlab-ci.yml`.

### Three reminders

- scanner jobs are **slow** on the first run: the runner downloads their images,
  and it must be able to reach the internet;
- an **empty** SAST report is a valid result: the scan ran and found nothing;
- removing the token from the code **does not erase** it from the history: treat
  it as compromised, therefore to be revoked.

### Validation

```bash
dsoxlab check gl-21-activer-les-scanners
```
