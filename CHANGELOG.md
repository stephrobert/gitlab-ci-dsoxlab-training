# Changelog

All notable changes to this catalog are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this catalog
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**What a version means here.** A catalog is not a library: a MINOR bump adds
labs, a PATCH fixes a statement or a test without changing what a lab proves,
and a MAJOR renames or removes labs, which breaks the progress already recorded
by learners.

## [0.1.1] - 2026-10-22

### Added

- A verdict can no longer be committed together with what it measures. The
  `verdicts-et-commun-separes` hook refuses a commit carrying
  `validation-labs.json` alongside anything the cycle plays:
  `challenge/tests/`, `setup.yaml`, `cleanup.yaml`, `lab.yaml` of any lab, plus
  the shared tooling.

  This closes a case **no measurement can catch afterwards**. When a squashed
  pull request touches a test *after* its campaign, the single commit carries
  both and the squash has destroyed what told them apart: neither a date, nor a
  diff between two trees, nor a fingerprint recorded later can say which came
  first. It cannot be observed, so it is prevented.

  The statement stays allowed next to a verdict: it is not played by the cycle,
  and forbidding it would demand a campaign for a typo.

- `scripts/empreinte_lab.py` and `scripts/verifier-attestations.py`, a local
  corroboration: a sha256 of what the cycle plays, recorded beside each verdict
  by future campaigns. It is **not required** — a verdict without one is not a
  defect, and the check says so and exits 0. `--strict` restores exit code 10
  for an automated caller.

### Fixed

- The staleness of a verdict is no longer judged by comparing **dates**, which
  answers a different question from the one being asked. It was wrong in both
  directions on 2026-10-22: a correction committed together with the verdicts
  it invalidated passed as healthy, and labs re-attested on a branch came back
  "to be re-attested" after their squash merge, their content unchanged.

  Git trees already are content fingerprints, so the authoritative check now
  compares two trees and no longer depends on how a branch was merged.

## [0.1.0] - 2026-10-22

### Added

- **Twenty-one labs on GitLab CI/CD**, `gl-01` to `gl-19` plus two end-of-level
  graded labs, `gl-ep1-un-pipeline-qui-dit-vrai` (C1) and
  `gl-ep2-une-livraison-tracable` (C2). Eleven hours fifty-five of labs, almost
  fourteen hours with the two graded ones.

- **Twenty-one verdicts VALIDE 0 -> 100** in `validation-labs.json`, each
  produced by `scripts/valider-labs.py`, which requires a score of ZERO on the
  starting state and one hundred on the corrected one. A test that passes
  before the work measures nothing, and this catalog made that mistake four
  times on its first day.

- **One VM**, `gitlab-1.lab`, carrying GitLab CE 19.5.1 and its runner, laid
  down by `labs/_commun/socle.yaml` in five minutes thirty-four on first pass
  and idempotent afterwards. The red-thread repository arrives as a git bundle,
  with `main` and the nineteen `starter/lab-NN` branches, never the `solution/`
  ones: a solution must not reach the forge that grades it.

- **Three checks of its own**, each born of a real defect.
  `scripts/check-playbooks.py` loads all eighty-seven playbooks, encrypted
  solutions included: it catches a defect that came back four times, a lone
  French apostrophe in a comment inside an `ansible.builtin.shell` block, which
  makes Ansible refuse the playbook with a message naming neither the file nor
  the cause. `scripts/check-tests.py` names the symbols neither imported nor
  defined in the tests. `dsoxlab validate-structure` holds the contract.

- **The contribution chain of the sibling catalogs**: Zizmor, Actionlint,
  Poutine, pre-commit parity and CodeQL on `python` and `actions`, plus
  Plumber, Scorecard, Dependabot and the issue templates. Six jobs, seven
  checks.

### Fixed

- `labs/_commun/depot/` is now out of reach of every hook. Measured while
  adding the `ruff` hook: the first pass of `trailing-whitespace` and
  `end-of-file-fixer` took **12 bytes** off the git bundle of the red-thread
  repository, from 67 018 to 67 006. `git bundle verify` still accepted it,
  which is worse than a clean failure: the day the cut falls elsewhere, the
  nineteen labs lose their starting repository with nothing to say so.

- The `playbooks-se-chargent` hook now names its dependency, `uv run --with
  pyyaml`, as the neighbouring hook already did. Without it the script ran with
  the system interpreter, where pyyaml is absent, could no longer tell a
  playbook from a task file, passed them all to `--syntax-check` and wrongly
  refused two. The hook failed while the same script passed on the command
  line.

- `ruff` is aligned on the rule set shared by the sibling catalogs instead of a
  narrower local one, and runs as a hook, not only in CI. Forty-nine gaps
  appeared. The forty-two that touched **attested tests** are dead
  `# noqa: E402` directives, left in place deliberately: replaying twenty-one
  labs on the forge to delete a comment is not a reasonable trade, and
  `per-file-ignores` says so in writing. The seven others, all in `scripts/`,
  are fixed.

## [Unreleased]

### Added

- The catalog skeleton, created by `dsoxlab new catalog`.
