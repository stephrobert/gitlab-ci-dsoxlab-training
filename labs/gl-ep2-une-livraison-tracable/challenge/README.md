# Exam: a delivery you can trace

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-ep2/pipeline-craft` on the VM, on branch `main`.

The chain builds, tests and deploys without leaving a trace. Four traces are
missing, and one of them blocks the others.

## Goal (expected state)

1. no job of the last pipeline on `main` is waiting, and none failed;
2. the project holds at least one **environment**, and at least one
   **successful deployment** is recorded there;
3. the project's **registry** holds at least one tag;
4. no production job started on its own on the default branch.

## No hints are provided

This is an exam: the four defects are not named, and there is no hint to
unlock. You have seen all of it in the four labs of this level.

## One constraint of this environment

This forge's registry answers over **HTTP**, not HTTPS. A Docker client
refuses by default to talk to a plain-text registry: the job's Docker service
has to declare the registry address as insecure. The starting pipeline already
does this; it is a given, not a defect.

## The commands that help you check

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft

# The real state of the last pipeline's jobs
PID=$(curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=1" | jq -r '.[0].id')
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines/$PID/jobs" \
  | jq -r '.[] | "\(.name) \(.status)"'

# What the project's runners offer, to compare with what the jobs ask for
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/runners" \
  | jq -r '.[] | "\(.description) \(.tag_list // [])"'

# The environments and the recorded deployments
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/environments" | jq -r '.[] | "\(.name) \(.state)"'
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/deployments" \
  | jq -r '.[] | "\(.environment.name) \(.status) \(.ref)"'

# The published images
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/registry/repositories" | jq -r '.[].id'
```

## Validation

```bash
dsoxlab check gl-ep2-une-livraison-tracable
```
