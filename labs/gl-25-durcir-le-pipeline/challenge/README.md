# Harden the runner

## The situation

The `pipeline-craft` pipeline is **green**. It runs a `tester` job, then two jobs
that play an attack each against the runner that executes them:

- `attaque-privilege` tries to mount a filesystem from inside the job. That needs a
  privileged container, and the job prints `ATTAQUE-REUSSIE`;
- `attaque-image` runs an image (`alpine:3.20`) nobody validated, and prints
  `ATTAQUE-REUSSIE` too.

Both jobs are green because **the attacks work**. A green attack job is the
problem, not the good news. They carry `allow_failure: true`, so a blocked attack
(a failed job) does not turn the whole pipeline red.

A runner is not hardened by a line of `.gitlab-ci.yml`. It is a **configuration the
runner holds**, in `/etc/gitlab-runner/config.toml` on the VM, a file owned by root.
The project is in the lab forge. A copy of the repository waits on the machine, with
a note: `NOTE-RUNNER.txt`.

## Mission

Three hardenings, then one proof.

1. **No more privileged mode.** A job must no longer hold full root access to the host.
2. **Allow only the images you use.** The legitimate pipeline uses
   `alpine:3.24.2@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6`
   and must keep running. `alpine:3.20` must be refused. A missing key allows every
   image, and a lone wildcard is not a list.
3. **Drop the Linux capabilities and forbid privilege gain.** Drop them all, and add
   the option that stops a process from gaining privileges.
4. **Prove it.** Run a pipeline on `main` and wait for it. `tester` must pass, and
   both attack jobs must have **failed on the refusal**, with the reason in their log.

Do not edit `.gitlab-ci.yml`: the attacks are the measure.

## What the lab checks

1. the runner is not privileged;
2. `allowed_images` exists, lets the legitimate image through and refuses `alpine:3.20`;
3. `cap_drop` contains `ALL` and `security_opt` contains `no-new-privileges:true`;
4. a pipeline ran on `main` since the start, and `tester` passed;
5. in that pipeline, `attaque-privilege` failed and its log says the attack was blocked;
6. in that pipeline, `attaque-image` failed and the runner refused the image.

The lab reads the runner configuration and the job logs. It does not impose the
patterns you write, as long as they cover the legitimate image and not the attack
image.

## Two limits to know

A hardened runner **cannot build an image with Docker-in-Docker**, which needs
`privileged = true`. The lab does not replay a build; the lesson explains the
alternatives. And the lab does not try every escape: it replays two, and a runner
that blocks them is not thereby proven safe.

## What is asked

### Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits in
`/opt/dsoxlab/gl-25/pipeline-craft` on the VM, on the `main` branch.

Its pipeline replays two attacks against the runner, and both succeed.

### Goal (expected state)

1. The runner is **not privileged**.
2. `allowed_images` is set, accepts the image of the legitimate pipeline and
   refuses `alpine:3.20`.
3. `cap_drop` contains `ALL`, `security_opt` contains `no-new-privileges:true`.
4. A pipeline ran on `main` after the hardening and `tester` passed.
5. In that pipeline both attack jobs **failed on the refusal**.

### Read before you start

`NOTE-RUNNER.txt`, next to the repository copy in `/opt/dsoxlab/gl-25`.

### Two reminders

- the runner configuration is a file owned by root: use `sudo`;
- do not edit `.gitlab-ci.yml`. A blocked attack is a failed job: read its log.

### Validation

```bash
dsoxlab check gl-25-durcir-le-pipeline
```
