# Scenario

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
4. the pipeline is **green**.

No test measures your method: the end state of a methodical person and that of
someone who guessed are identical. The method is the lab's subject, not its
score.
