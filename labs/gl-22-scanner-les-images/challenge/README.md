# Challenge: scan the image, and stop shipping a critical flaw

## Mission

The `pipeline-craft` project is in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-22/pipeline-craft` on the VM, on branch `main`.

Its pipeline publishes the image to the project registry and never scans it.
The image still carries a critical vulnerability.

## Goal (expected state)

1. The latest pipeline on `main` has a scan job, and its **Trivy JSON report**
   is kept in the artifacts.
2. That report is about **this project's image, at the commit's tag**.
3. A pipeline **failed because of a critical**, report kept, with no deployment
   at all.
4. `.trivyignore` rules out **the finding the security team triaged, and only
   that one**, with its **reason** written above it.
5. The latest report **no longer lists** that finding.

## Read before starting

Two notes wait next to the repository copy, in `/opt/dsoxlab/gl-22` (both in
French):

- `REGISTRE-DU-LAB.txt`: the registry answers over HTTP and the project is
  private;
- `NOTE-EQUIPE-SECURITE.txt`: the ruled-out finding, and why.

## Trivy image

`aquasec/trivy:0.58.1@sha256:ab70a02200597efa04748f210f793936eb647cbcdb0ea69cc30b226d6f5a22c7`, which declares an entrypoint to neutralise
(`entrypoint: [""]`) so that GitLab can run the job's script.

## Four reminders

- a new stage must be **declared** in `stages:`, otherwise GitLab refuses the
  whole configuration and the pipeline is born `failed` with not a single job;
- a failed job does **not** keep its artifacts without `when: always`;
- an exception is **justified** next to the identifier, and only covers the
  triaged finding;
- a red pipeline at the end is normal as long as other criticals remain.

## Validation

```bash
dsoxlab check gl-22-scanner-les-images
```
