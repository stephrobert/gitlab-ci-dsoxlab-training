# Exam: a pipeline that tells the truth

## The situation

This is the level 1 exam. There is no step-by-step guide, no hint, and the
defects are not named.

The project's pipeline is **green**. It runs, it complains about nothing, and
the team has trusted it for weeks.

Yet it guarantees almost none of what it shows. This pipeline makes four
promises, and none of them is kept:

1. "the tests pass";
2. "the results can be read";
3. "the deployment token is protected";
4. "production is under control".

The project is in the lab forge. A copy of the repository is waiting for you on
the machine.

## Mission

Make the pipeline honest: each of those four promises has to become true, and
verifiable by someone who did not write the pipeline.

That is the point of the exam, and it is also the skill of the level: a
pipeline is not there to be green, it is there to **tell the truth about the
state of the code**. A green pipeline that guarantees nothing is worse than a
red one, because nobody comes to look at it.

## How to look

You have seen all of it in the seven labs of this level. Three reflexes are
enough:

- **read the configuration as a reviewer**, not as its author: what promise
  does each job make, and what would stop that promise from being false?
- **ask GitLab**, not the file. The project's CI linter returns the
  **compiled** configuration, and the API says what the server really
  produced: test results, variables, pipelines per branch;
- **try it**. A pipeline property that depends on a branch cannot be read, it
  is measured by pushing a branch.

## What the exam grades

It grades **the state left in the forge**, never the commands typed:

1. no test job is allowed to fail, and they really succeeded;
2. the pipeline's test report is not empty on GitLab's side;
3. no form of secret remains in the compiled configuration, and the project
   holds at least one **masked** variable;
4. a pushed working branch triggers **no** deployment job.

## What the exam does not grade

Not the name of your variable, not how you protect production, not the tool
that produces the report. There is more than one right answer, and a working
branch that triggers no pipeline at all is one of them.

## One warning, because it matters

The fourth check **pushes a branch** from the machine's working copy to measure
what the forge protects, then deletes it. If you are working on a branch called
`essai-de-l-epreuve` yourself, rename it.

## What is asked

### Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-ep1/pipeline-craft` on the VM, on branch `main`.

The pipeline is green. It makes four promises and keeps none of them. It is up
to you to find which, and to make them true.

### Goal (expected state)

1. no test job is allowed to fail, and they really succeeded;
2. the pipeline's test report is not empty on GitLab's side;
3. no secret remains in the compiled configuration, and the project holds at
   least one **masked** variable;
4. a pushed working branch triggers no deployment job.

### No hints are provided

This is an exam: the four defects are not named, and there is no hint to
unlock. You have seen all of it in the seven labs of this level.

### The commands that help you check

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

### Validation

```bash
dsoxlab check gl-ep1-un-pipeline-qui-dit-vrai
```
