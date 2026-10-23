# Scenario

The `pipeline-craft` pipeline builds an image and publishes it to the project
registry, under the commit's tag. Nobody looks at it.

It still shipped to production on an old base, and that base carries a known
**critical vulnerability**. Nothing in the pipeline said so, nothing stopped it:
the image was built, published, and the deployment followed.

The project is in the lab forge. A copy of the repository waits for you on the
machine, with two notes: `REGISTRE-DU-LAB.txt` and `NOTE-EQUIPE-SECURITE.txt`
(both written in French).

## Mission

Four steps, each one relying on the previous.

1. **Scan the published image.** A job reads the image the pipeline has just
   pushed, and writes a report.
2. **Keep the report.** It must stay readable in the forge, including when the
   job fails, since that is when you need it.
3. **Block.** A critical vulnerability fails the pipeline before any deployment.
4. **Rule out what was ruled out, and only that.** The security team triaged
   one of the findings. Record its exception, with its reason.

## Why Trivy, and not GitLab's Container Scanning

This catalogue's instance is a **GitLab CE**. The built-in Container Scanning
does produce its report there, but everything that makes use of it (security
dashboard, project vulnerability report, merge request policies) is reserved to
the Premium and Ultimate editions. This lab therefore works with what the
Community Edition really gives you: **a JSON artifact** in the job, which you
read yourself. The scanner is **Trivy**, on the command line.

Image to use: `aquasec/trivy:0.58.1@sha256:ab70a02200597efa04748f210f793936eb647cbcdb0ea69cc30b226d6f5a22c7`.

## What Trivy needs to know

| Option or variable | What it does |
|---|---|
| `--format json --output <file>` | writes the full report as JSON |
| `--severity CRITICAL` | limits the analysis (and the threshold) to one severity |
| `--exit-code 1` | fails the command if findings remain |
| `--insecure` | allows a registry that answers over HTTP |
| `TRIVY_USERNAME`, `TRIVY_PASSWORD` | the registry credentials, which the job already has |

The registry details are in `REGISTRE-DU-LAB.txt`. This forge's registry
answers over **HTTP**, and the project is private: a Trivy that does not know
this fails before scanning anything.

## The lost-report trap

By default, GitLab **does not keep the artifacts of a failed job**. But the scan
job is meant to fail: without a setting, the pipeline stops, and the report that
explains why disappears with it. You see the red, you do not have the cause.

The lab therefore checks that the report survives the failure, and that the
pipeline really failed **because of a critical vulnerability**, not because of
an unreachable registry.

## The exception trap

Ruling out a finding makes the problem disappear from the report without fixing
it. An attacker hopes for nothing else: an exception line without explanation
passes review, and six months later nobody remembers why it is there.

Trivy reads exceptions from a **`.trivyignore`** file at the repository root.
Two rules for this lab:

- **the reason is written next to the exception**, on the comment lines (`#`)
  that precede the identifier;
- **only the triaged finding is ruled out**. The other critical vulnerabilities
  have been examined by nobody. Ignoring them to make the pipeline pass is
  exactly what this lab teaches you to recognise.

`NOTE-EQUIPE-SECURITE.txt` gives the ruled-out identifier and the review's
reason. That note is the lab's **premise**. In a real team you would check
before ruling out: is the package in the image, is the vulnerable code
reachable? Here you restate the reason in your own words, making sure it holds
against what the report shows for that finding.

## A red pipeline at the end is normal

Once the triaged finding is ruled out, **the other criticals remain**. The
threshold keeps stopping the pipeline: that is its job. Really fixing it means
moving the **image base** to an up-to-date version, which is the right next step
but is not graded here.

A pipeline that only passes because everything was ruled out would be a
regression.

## What the lab checks

1. the **latest pipeline** on `main` has a scan job that left a **Trivy JSON
   report** in its artifacts;
2. that report is about **this project's registry image, at the tag of this
   pipeline's commit**;
3. a pipeline **really failed** because of a critical vulnerability, with a kept
   report, and **no deployment** started;
4. `.trivyignore` rules out **the triaged finding and only that one**, with a
   **reason** of at least four words;
5. the **latest report no longer lists** that finding.

## What the lab does not check

Not your job's name, not your stage's name, not the report file's name. Not
that the reason you write is **true** either: an automatic check measures that
it exists, not that it is right. That is a human review's job.

## Checking by hand

A job's artifacts can be read in the project interface, or from the VM:

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=3" \
  | jq -r '.[] | "\(.id) \(.status) \(.sha[0:8])"'
```

Then, to list the critical findings of a downloaded report:

```bash
jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")
  | "\(.VulnerabilityID) \(.PkgName) \(.InstalledVersion)"' trivy-report.json
```

Replace `trivy-report.json` with the name you gave your file.
