# GitLab CI/CD Training: write a pipeline, and prove what it does

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/gitlab-ci-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/gitlab-ci-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/gitlab-ci-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/gitlab-ci-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/gitlab-ci-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/gitlab-ci-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Twenty-one hands-on labs to write a GitLab CI/CD pipeline and keep it
trustworthy: make it green, read its failures, move data between jobs, take the
secrets out of the code, control when it runs, publish to the registry, then
industrialise it. Every lab runs against a **real GitLab CE instance and its
runner**, and is graded on the state of the pipeline it leaves behind, never on
the commands typed.

Written for sysadmins and DevOps engineers who inherit a pipeline they did not
write and have to keep it running.

## What it is

At the end, a learner can take a repository with no CI at all and return a
pipeline that builds, tests and publishes, that says what it covers, that runs
once per change rather than twice, and that fails loudly rather than quietly.
Each of those is proven by tests that question the forge through its API, not
by reading the `.gitlab-ci.yml` the learner wrote.

**The order matters, and it is not the order of the topics.** It follows what a
pipeline needs before the next step is even possible: a green pipeline before
reading a failure, a failure read before choosing an image, artifacts before
publishing, publishing before industrialising. Level 2 assumes a pipeline that
works and asks what happens when it misbehaves; level 3 assumes you can repair
one and asks how to make it fast, factored and reliable.

`dsoxlab next` follows that order, derived from the position of each lab in
`meta.yml`.

### What the tests do, and what they refuse to do

**A lab is graded on the state left on the forge, never on the commands typed.**

The tests question GitLab through its API: the pipelines that really ran, their
jobs, their statuses, the registry tags, the reports attached to a merge
request. They do not read the YAML the learner wrote.

```python
# NO: we re-read what the learner wrote, which proves nothing
assert "needs:" in gitlab_ci_yml

# YES: we ask the forge what actually happened
jobs = api(f"/projects/{pid}/pipelines/{pipeline}/jobs")
assert {j["name"] for j in jobs if j["status"] == "success"} >= attendus
```

The trap this avoids is a green pipeline that does nothing. A `.gitlab-ci.yml`
with a single `echo ok` job passes and proves nothing, so the exams require
several successful jobs covering distinct steps, deduced from the job logs and
not from their names.

## Requirements

A missing requirement costs the learner an hour of searching, so this list is
exact and measured against `meta.yml`.

- **Python 3.11+ and [`uv`](https://docs.astral.sh/uv/)**
- **`git`**
- **`dsoxlab`**, the engine, installed as a standalone tool (see below)
- **`terraform`** and **`ansible-playbook`**, which every `vm` lab needs
- **libvirt/KVM 8.0 or above**, the hypervisor the machine runs on

Nothing GitLab-related is needed on your own machine: the lab installs GitLab
CE and its runner inside the virtual machine, which is the subject of the
common base played before the first lab.

**All twenty-one labs are `vm` labs**, so `dsoxlab provision` is always needed.

### The machine, and why it is a large one

One virtual machine, declared in [`meta.yml`](./meta.yml) on the
`lab-gitlab-ci` network (`10.10.95.0/24`):

| Host | Distribution | vCPU | RAM | Disk |
|---|---|---|---|---|
| `gitlab-1.lab` | Ubuntu 24.04 | 4 | 8 GB | 50 GB |

GitLab CE is not a small service: 8 GB of RAM and 4 vCPU are what it takes for
its own components, its runner, and the containers the jobs start. The base is
laid down by `labs/_commun/socle.yaml` in about five and a half minutes on
first pass, and is idempotent afterwards.

The red-thread repository arrives as a **git bundle**, with `main` and the
nineteen `starter/lab-NN` branches. The `solution/` branches are never pushed:
a solution has no business in the forge that grades it.

`dsoxlab doctor` says what this repository needs and what it does not, and
tells apart a check that failed from one it could not measure.

## Install

`dsoxlab` is published on [PyPI](https://pypi.org/project/dsoxlab/). Install it
as a standalone tool, so it stays out of this repository:

```bash
# 1. The dsoxlab CLI (external tool, stays out of this repo)
uv tool install dsoxlab

# 2. This lab catalog
git clone https://github.com/stephrobert/gitlab-ci-dsoxlab-training.git
cd gitlab-ci-dsoxlab-training

# 3. Check the contract and the machine
dsoxlab validate-structure
dsoxlab doctor
```

### Your first lab, in five minutes

The machine has to exist first: nothing here runs on your own host.

```bash
export LAB_HOME=$PWD
dsoxlab provision                        # creates gitlab-1.lab, once

dsoxlab list-labs                        # the twenty-one labs, in teaching order
dsoxlab run       gl-01-premier-pipeline # sets the starting state and opens the session
dsoxlab challenge gl-01-premier-pipeline # read the mission, no step-by-step
dsoxlab check     gl-01-premier-pipeline # run the tests, record the score

dsoxlab clean     gl-01-premier-pipeline # undoes the lab, keeps the machine
dsoxlab destroy                          # gives the machine back
```

`run` is what prepares the lab. Running `check` on a lab you never started
measures nothing, and says so rather than recording a 0. `provision` exits
non-zero if the host does not answer, and names the orphan domains it left
behind rather than claiming success.

### Keeping it up to date

```bash
uv tool upgrade dsoxlab        # the engine, published on PyPI
git -C <this repo> pull        # the catalog
```

The engine and the catalog move independently: a new `dsoxlab` never requires
re-cloning the labs, and new labs never require upgrading the tool, as long as
the contract version matches.

## How it works

### The declarative contract (two levels)

This repository is **not the CLI**. An engine defect is fixed in
[dsoxlab](https://github.com/stephrobert/dsoxlab), or reported as an issue
there. Here, everything driving the CLI is declarative:

- **`meta.yml`** at the root declares the repository identity, the
  **infrastructure** (provider, network `lab-gitlab-ci`, `10.10.95.0/24` and the
  host `gitlab-1.lab`) and the **order** of the sections shown by `list-labs`;
- **`lab.yaml`** per lab declares its `skills`, `level`, `runtime`, `distros`,
  `doc_url` and a `validation` block. A `lab.fr.yaml` overrides `title` and
  `description` in French, and nothing else;
- **`setup.yaml`** and **`cleanup.yaml`** lay down and undo the forge state;
- **`challenge/tests/test_functional.py`** carries the proof.

The Terraform and cloud-init templates are **packaged inside dsoxlab**, not
here: this repository declares only its `infra:` block and its public key in
`ssh/`.

### The lab lifecycle

```bash
dsoxlab list-labs              # browse the catalog
dsoxlab show      <id>         # metadata and status of one lab
dsoxlab run       <id>         # lay down the initial state and open the session
dsoxlab challenge <id>         # read the mission, no step-by-step
dsoxlab hint      <id>         # reveal a hint (deducted from the score)
dsoxlab check     <id>         # run the tests, compute and record the score
dsoxlab submit    <id>         # for the two exams: a verdict, not a bare score
dsoxlab clean     <id>         # undo the lab, keep the machine
dsoxlab progress               # per-section progress, average score
```

### The validation model

Validation **proves the state, it does not trust the learner**, and a lab is
proven **in both directions**: the tests must fail before the work and pass
after it. A test that is green before the work is not a test, it is an
assumption about the setup. This catalog made that mistake four times on its
first day, which is why `scripts/valider-labs.py` requires **0 before and 100
after** and records the verdict in [`validation-labs.json`](./validation-labs.json).

The reference solutions live in `solution/<lab>/solution.yaml`, and **all
twenty-one are encrypted** with `ansible-vault`. A solution shipped in clear
text spoils the lab, and git keeps it forever.

Three checks of this repository's own, each born of a real defect:

| Check | What it caught |
|---|---|
| `scripts/check-playbooks.py` | a lone French apostrophe in a comment inside an `ansible.builtin.shell` block makes Ansible refuse the playbook, with a message naming neither the file nor the cause. It came back four times. |
| `scripts/check-tests.py` | a symbol neither imported nor defined in a test: it raises at run time and scores the learner 0, with nothing accusing the test. |
| `dsoxlab validate-structure` | the declarative contract, links, scale and language parity. |

## Catalog

Twenty-one labs, **13 h 55** in all, across four levels that follow the course
they validate.

### Level 1: write a pipeline and read its failures

Seven labs and an exam, 5 h 05.

| Lab | What it proves |
|---|---|
| `gl-01-premier-pipeline` | a pipeline really ran on the default branch, green, with at least three successful jobs over several stages |
| `gl-02-lire-un-echec` | the failure is read in the job log and fixed, not worked around |
| `gl-03-images-et-runners` | each job runs on the image its work needs, and the runner picks it up |
| `gl-04-artifacts-et-cache` | the dependencies are cached and the test report survives the job |
| `gl-05-sortir-les-secrets` | no secret remains in the repository, and the pipeline still works |
| `gl-06-controler-execution` | each job runs when it should, and the deploy is held back |
| `gl-07-valider-avant-de-pousser` | the pipeline is validated before it reaches the forge |
| `gl-ep1-un-pipeline-qui-dit-vrai` | **graded**: four defects to find in a pipeline that looks green |

### Level 2: deliver

Four labs and an exam, 3 h 10.

| Lab | What it proves |
|---|---|
| `gl-08-declencher-autrement` | a pipeline starts by schedule, by API and from another project |
| `gl-09-publier-au-registre` | the image is in the registry, carrying the commit tag |
| `gl-10-rapports-de-qualite` | the reports show up where the reviewer looks |
| `gl-11-diagnostiquer-un-job-bloque` | two silent failures: nothing runs, and nothing complains |
| `gl-ep2-une-livraison-tracable` | **graded**: a delivery that can be traced back to its commit |

### Level 3: industrialise

Eight labs, 5 h 40.

| Lab | What it proves |
|---|---|
| `gl-12-accelerer-le-pipeline` | a cache that is really reused, and jobs that stop waiting for nothing |
| `gl-13-factoriser-le-yaml` | the pipeline stops repeating itself, without changing what it does |
| `gl-14-externaliser-les-jobs` | one orchestrator, one file per stage |
| `gl-15-une-matrice-de-tests` | more than one combination tested at a time |
| `gl-16-un-pipeline-enfant` | a pipeline that generates and runs its own jobs |
| `gl-17-un-seul-pipeline-par-changement` | one change, one pipeline, not two |
| `gl-18-fiabiliser-sans-masquer` | reliable without hiding failures behind a retry |
| `gl-19-reconstruire-tout-le-pipeline` | the whole pipeline rebuilt from scratch |

### Level 4: secure and tool

**Empty, and declared as such.** This is the gap the audit of 2026-10-21 found:
the whole level, seven security lessons and three on tooling, has no hands-on
practice yet. Saying so in the catalog is better than letting a learner
discover it halfway through.

## Contributing

Read [`CONTRIBUTING.md`](./CONTRIBUTING.md). In short: a lab is proven **in both
directions** before it is merged, `dsoxlab validate-structure` is green, and the
statement exists in English and in French.

A verdict is never committed together with the shared code it measures: the
staleness check compares commit dates, and a verdict written in the same commit
as `labs/_commun/` leaves nothing to compare. A hook enforces it.

## License

See [`LICENSE`](./LICENSE).
