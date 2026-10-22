# Challenge: rebuild the whole pipeline

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-19/pipeline-craft` on the VM, on branch `main`.

The repository has **no CI file at all**. The specification is in
`CAPSTONE-LAB-19.md`, at the root of the repository.

## Goal (expected state)

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

## Before you start: this environment's registry

It answers over HTTP. The memo `/opt/dsoxlab/gl-19/REGISTRE-DU-LAB.txt` gives
the line to write so the job's Docker service agrees to talk to it.

## The four commands that help you check

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

## Validation

```bash
dsoxlab check gl-19-reconstruire-tout-le-pipeline
```
