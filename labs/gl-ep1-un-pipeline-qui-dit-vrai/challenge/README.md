# Exam: a pipeline that tells the truth

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-ep1/pipeline-craft` on the VM, on branch `main`.

The pipeline is green. It makes four promises and keeps none of them. It is up
to you to find which, and to make them true.

## Goal (expected state)

1. no test job is allowed to fail, and they really succeeded;
2. the pipeline's test report is not empty on GitLab's side;
3. no secret remains in the compiled configuration, and the project holds at
   least one **masked** variable;
4. a pushed working branch triggers no deployment job.

## No hints are provided

This is an exam: the four defects are not named, and there is no hint to
unlock. You have seen all of it in the seven labs of this level.

## The commands that help you check

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft

# What GitLab understood of your configuration, inheritance resolved
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/ci/lint?dry_run=true&ref=main" \
  | jq -r '.valid, .errors[]?'

# The test results as the server sees them
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/test_report" \
  | jq '{total_count, failed_count}'

# The project's variables, and whether they are masked
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/variables" \
  | jq -r '.[] | "\(.key) masked=\(.masked)"'

# What a branch really triggers
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=<branch>" \
  | jq -r '.[0].id'
```

## Validation

```bash
dsoxlab check gl-ep1-un-pipeline-qui-dit-vrai
```
