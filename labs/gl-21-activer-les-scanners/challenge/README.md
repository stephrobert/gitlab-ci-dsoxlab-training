# Challenge: turn the scanners on, and read what they say

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits in
`/opt/dsoxlab/gl-21/pipeline-craft` on the VM, on branch `main`.

The pipeline runs the tests and nothing else. Turn on SAST and Secret Detection,
read the reports, fix the defect they point at.

## Goal (expected state)

1. A **SAST** job succeeded and left its report.
2. A **Secret Detection** job succeeded and left its report.
3. A Secret Detection report **points at the token** written in the code.
4. The token is **no longer in the code**, and the pipeline of the last commit of
   `main`, started by a push, confirms it.
5. `LECTURE.md`, at the root of `main`, names **the file and the line** from the
   report.

## The three steps

1. add both templates and wait for the pipeline;
2. read the reports, including the one from a history scan;
3. fix, push, and let the push pipeline confirm.

## The lab runs on a Community edition

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

## If the scan does not see the token

A push scan examines the commits it receives, and the token is older. A pipeline
started by hand re-reads the history: **Build > Pipelines > New pipeline**,
branch `main`, variable `SECRET_DETECTION_HISTORIC_SCAN` set to `true`. It is a
**one-off** operation, never to be left in `.gitlab-ci.yml`.

## Three reminders

- scanner jobs are **slow** on the first run: the runner downloads their images,
  and it must be able to reach the internet;
- an **empty** SAST report is a valid result: the scan ran and found nothing;
- removing the token from the code **does not erase** it from the history: treat
  it as compromised, therefore to be revoked.

## Validation

```bash
dsoxlab check gl-21-activer-les-scanners
```
