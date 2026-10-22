# Challenge: one change, one pipeline

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-17/pipeline-craft` on the VM, on the `main` branch.

A branch carrying an open merge request starts two pipelines for the same
commit.

## Goal (expected state)

1. An **open merge request** exists, from a branch other than the default one.
2. On the **last commit of that branch**, there is only **one** pipeline, and
   its source is `merge_request_event`.

## The three steps

1. fix the `workflow:`;
2. push a branch and **open the merge request**;
3. push a commit **after** opening it: that is the one being measured.

## Two reminders

- GitLab stops at the **first matching rule**. A refusal rule placed too high
  also closes the merge request;
- the request must be open **before** the measured push, otherwise the variable
  GitLab consults is empty when it evaluates the rules.

## Counting a commit's pipelines

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
SHA=$(git rev-parse HEAD)
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?sha=$SHA" \
  | jq -r '.[] | "\(.id) \(.source) \(.status)"'
```

## Validation

```bash
dsoxlab check gl-17-un-seul-pipeline-par-changement
```
