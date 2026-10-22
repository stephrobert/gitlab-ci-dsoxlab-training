# Challenge: lock the branch, the tags and the merge

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits in
`/opt/dsoxlab/gl-24/pipeline-craft` on the VM, on the `main` branch.

Its pipeline is green and deploys to `production`. The project carries no lock.

## Goal (expected state)

1. `main` is **protected**: Developers cannot push to it, force push is off,
   and someone can merge into it.
2. A **protected tag** pattern covers `v1.0.0`; only Maintainers create it.
3. Merging **requires a successful pipeline**.
4. Merging **requires resolved discussions**.
5. A pipeline has run on `main` since the start and both jobs, `tester` and
   `deployer-production`, passed.

## Read before you start

`NOTE-VERROUS.txt`, next to the repository copy in `/opt/dsoxlab/gl-24`.

## Two reminders

- a lock is a setting of the forge: nothing in `.gitlab-ci.yml` creates it;
- run the proof pipeline **after** setting the locks: the forge does not date
  them, the lab cannot see the order, you can.

## Validation

```bash
dsoxlab check gl-24-proteger-les-merges
```
