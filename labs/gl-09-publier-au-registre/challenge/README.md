# Challenge: publish the image, and keep it traceable

## Mission

The `pipeline-craft` project lives in the lab forge, at
`http://gitlab-1.lab/root/pipeline-craft`, and a copy of the repository waits
in `/opt/dsoxlab/gl-09/pipeline-craft` on the VM, on the `main` branch.

Its pipeline builds an image and throws it away. The project registry is empty.

## Goal (expected state)

1. The project registry holds **at least one image**.
2. A published tag carries the **short SHA of the last commit**.
3. A successful job's log shows the push.
4. No job failed.

## The variables GitLab hands you

| Variable | What it holds |
|---|---|
| `$CI_REGISTRY` | the instance registry's address |
| `$CI_REGISTRY_IMAGE` | this project's full image path |
| `$CI_REGISTRY_USER` and `$CI_REGISTRY_PASSWORD` | disposable credentials, valid for the job |
| `$CI_COMMIT_SHORT_SHA` | the short SHA of the commit that started the pipeline |

Checking the result, from the VM:

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
curl -s -H "PRIVATE-TOKEN: $JETON" \
  "http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft/registry/repositories?tags=true" \
  | jq '.[] | {path, tags: [.tags[].name]}'
```

The UI shows the same under **Deploy > Container Registry**.

## Validation

```bash
dsoxlab check gl-09-publier-au-registre
```
