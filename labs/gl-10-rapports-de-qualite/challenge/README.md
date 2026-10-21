# Challenge: make the pipeline say what it covers

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-10/pipeline-craft` on the VM, on the `main` branch.

Its pipeline publishes the test report, and nothing about coverage.

## Goal (expected state)

1. A non-zero **coverage** reached GitLab.
2. A **coverage report** is published as an artifact, the test report is still
   filled, and no job failed.

## What the repository already provides

`requirements-dev.txt` installs **pytest-cov**: the tool is there, it is not
wired. The package to cover is `app`.

Checking that the fishing worked, from the VM:

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID" | jq '{coverage}'
```

A `null` means the regular expression found nothing, without anything having
failed.

## Validation

```bash
dsoxlab check gl-10-rapports-de-qualite
```
