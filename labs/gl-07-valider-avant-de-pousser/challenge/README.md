# Challenge: validate before you push

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-07/pipeline-craft` on the VM, on the `main` branch.

Its pipeline is red with **no job at all**: the configuration is refused.

## Goal (expected state)

1. GitLab **accepts** the configuration.
2. No **three-star** pattern is left in the merged configuration.
3. The test job **ran and passed**.
4. **No job in the pipeline failed.** Its status will be **`manual`**: the
   production deployment awaits its decision.

## Validating without pushing

```bash
# From the VM, the lint API on the chosen branch:
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/ci/lint?dry_run=true&ref=main" \
  | jq '{valid, errors}'
```

The pipeline editor (`Build > Pipeline editor`) says the same in the UI, and the
API response also carries `merged_yaml`, the configuration GitLab actually
understood.

## Validation

```bash
dsoxlab check gl-07-valider-avant-de-pousser
```
