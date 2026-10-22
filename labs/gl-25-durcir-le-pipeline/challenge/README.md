# Challenge: harden the runner

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits in
`/opt/dsoxlab/gl-25/pipeline-craft` on the VM, on the `main` branch.

Its pipeline replays two attacks against the runner, and both succeed.

## Goal (expected state)

1. The runner is **not privileged**.
2. `allowed_images` is set, accepts the image of the legitimate pipeline and
   refuses `alpine:3.20`.
3. `cap_drop` contains `ALL`, `security_opt` contains `no-new-privileges:true`.
4. A pipeline ran on `main` after the hardening and `tester` passed.
5. In that pipeline both attack jobs **failed on the refusal**.

## Read before you start

`NOTE-RUNNER.txt`, next to the repository copy in `/opt/dsoxlab/gl-25`.

## Two reminders

- the runner configuration is a file owned by root: use `sudo`;
- do not edit `.gitlab-ci.yml`. A blocked attack is a failed job: read its log.

## Validation

```bash
dsoxlab check gl-25-durcir-le-pipeline
```
