# Challenge: protected secrets, in a file, and renewed

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits in
`/opt/dsoxlab/gl-20/pipeline-craft` on the VM, on the `main` branch (protected).

Two jobs, `joindre-le-service` and `installer-la-cle`, consume the variables
`SERVICE_TOKEN` and `DEPLOY_KEY`. Both are badly managed.

## Goal (expected state)

1. `SERVICE_TOKEN` is **protected** and **masked**.
2. `DEPLOY_KEY` is a **file-type** variable, **protected**, with its value
   unchanged.
3. Token `service-v1` is **revoked**. `SERVICE_TOKEN` holds **another** valid
   token, and `joindre-le-service` has never failed since the start.
4. The latest pipeline on `main` is healthy, both jobs pass, and the log of
   `installer-la-cle` shows `CLE-SOURCE=fichier` (a line of the starting job, to
   be kept).

## Read before you start

`NOTE-SECRETS.txt`, next to the repository copy in `/opt/dsoxlab/gl-20`.

## Four reminders

- a file-type variable puts the **path** of a file in the variable, not the
  value: the job must read that file;
- changing the variable type without adapting the job breaks the pipeline: both
  changes go together;
- a job that fails after the type of `DEPLOY_KEY` changes is not a forge outage:
  it still reads the value where it now receives a path;
- the API `rotate` route creates the new token and revokes the old one in a
  single move: there is then no time to put the new one in service.

## Validation

```bash
dsoxlab check gl-20-secrets-avances
```
