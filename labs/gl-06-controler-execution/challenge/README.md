# Challenge: decide when the pipeline runs

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-06/pipeline-craft` on the VM, on the `main` branch.

All of its jobs run on every push, on any branch, and nothing is deployed.

## Goal (expected state)

1. A deployment job **succeeded** automatically on the default branch.
2. Another deployment job waits for a **human decision** (`manual` status).
3. The pipeline stays **green**.
4. The configuration carries a **`workflow:`** block.

The repository ships `scripts/deploy-demo.sh <environment>`, which simulates a
deployment: no need to write one.

## What is not imposed

Neither the job names, nor the deployment stage name, nor the exact conditions
of your rules, as long as the four points above hold.

## Validation

```bash
dsoxlab check gl-06-controler-execution
```
