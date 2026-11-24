# Validate before you push

## The situation

Someone changed `pipeline-craft`'s `.gitlab-ci.yml`, and the pipeline is red.
Not red as in "a job failed": red with **no job at all**. GitLab refused the
configuration before creating a single one.

The team got used to guessing a fix and pushing to see. Every attempt costs a
commit in the history, a slot in the runner queue, and a few minutes of
waiting. By the third round trip, nobody knows which version is live.

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Find the faults **before** pushing, then push once.

Three faults await you, and they are not of the same kind. That difference
matters more than the fixes themselves:

- the first makes the configuration **refused**. GitLab reports it itself, and
  its message names the cause;
- the second is **hidden by the first**: while the configuration is refused,
  nothing is evaluated, so nothing else can be reported;
- the third one GitLab **accepts**. It shows up neither in the refusal nor at
  run time. An accepted file is not thereby a correct one.

## Validating without pushing

GitLab will tell you what it thinks of a configuration without running it:

- the **pipeline editor** (`Build > Pipeline editor`) validates the chosen
  branch's file and shows the error;
- the **lint API** answers the same in one request, and also returns the
  **merged** configuration, the one GitLab actually understood after resolving
  includes and anchors;
- `glab ci lint`, if you have the CLI, does the same from the terminal.

## What the lab checks

1. GitLab **accepts** the configuration;
2. no **three-star** pattern is left in the merged configuration;
3. the test job **ran and passed**, which closes the first two faults at once;
4. **no job in the pipeline failed**. The pipeline's status will be
   **`manual`**, the production deployment inherited from the previous lab
   awaiting its decision.

No test measures your method: the end state of a methodical person and that of
someone who guessed are identical. The method is the lab's subject, not its
score.

## What is asked

### Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-07/pipeline-craft` on the VM, on the `main` branch.

Its pipeline is red with **no job at all**: the configuration is refused.

### Goal (expected state)

1. GitLab **accepts** the configuration.
2. No **three-star** pattern is left in the merged configuration.
3. The test job **ran and passed**.
4. **No job in the pipeline failed.** Its status will be **`manual`**: the
   production deployment awaits its decision.

### Validating without pushing

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

### Validation

```bash
dsoxlab check gl-07-valider-avant-de-pousser
```
