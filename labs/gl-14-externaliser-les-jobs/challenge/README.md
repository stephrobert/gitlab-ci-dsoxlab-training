# Challenge: one orchestrator, one file per stage

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-14/pipeline-craft` on the VM, on the `main` branch.

Its pipeline is eighty lines long, and all of it is correct.

## Goal (expected state)

1. GitLab reports **at least two included files**.
2. The behaviour has not moved: no failed job, at least four successful ones,
   and coverage still reported.
3. The merged configuration still carries `stages:` and `workflow:`.

## Two things to know

- included files **do not compartmentalise**: a hidden job declared in one is
  visible from another, GitLab merging everything before evaluating;
- a **YAML anchor** does not cross files. It must live in the same file as its
  `<<:`.

## Checking what GitLab included

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/ci/lint?dry_run=true&ref=main" \
  | jq '{valid, includes}'
```

A badly written `include:` does not always raise an error: it may simply
include nobody.

## Validation

```bash
dsoxlab check gl-14-externaliser-les-jobs
```
