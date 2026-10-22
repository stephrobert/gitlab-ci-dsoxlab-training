# Challenge: reliable without hiding failures

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-18/pipeline-craft` on the VM, on branch `main`.

The pipeline is "failed" with not a single job. Repair it, then make it
reliable.

## Goal (expected state)

1. GitLab **accepts** the configuration of `main`, and a pipeline runs there
   with its jobs.
2. Every deployment job carries a **lock**, and the forge really holds those
   locks.
3. A **retry** exists, and **none** of them covers a script failure.
4. Deployments carry a **timeout** and are **no longer cancellable**.

## The two steps

1. find out why GitLab refuses the configuration, and fix it;
2. add the retry, the timeouts, the locks and the ban on cancelling.

## When the pipeline says nothing, ask the linter

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/ci/lint?dry_run=true&ref=main" \
  | jq -r '.valid, .errors[]?'
```

The same call serves at the end: when it answers `true`, it also returns the
**compiled** configuration, the one the lab grades.

## See the locks the forge created

```bash
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/resource_groups" \
  | jq -r '.[] | "\(.key) \(.process_mode)"'
```

The list is empty at the start. A lock only exists from the moment a pipeline
carrying it has been created: push your configuration before counting.

## Two reminders

- a retry that covers a script failure turns a flaky test into a test that
  eventually passes **by chance**. Reasons are named one by one;
- the main file allows **every** job to be cancelled. For a deployment, that
  has to be undone job by job.

## Validation

```bash
dsoxlab check gl-18-fiabiliser-sans-masquer
```
