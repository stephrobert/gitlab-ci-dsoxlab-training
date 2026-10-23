"""Tests du lab gl-25-durcir-le-pipeline.

CE LAB NOTE DEUX CHOSES QUE LE DEPART NE PORTE PAS : la configuration du
RUNNER (/etc/gitlab-runner/config.toml) et ce que les jobs d'attaque ont
reellement obtenu. Le runner est le seul a appliquer ces reglages, et un
`.gitlab-ci.yml` ne les contient pas.

LA REGLE DU CATALOGUE : l'etat de depart est un runner OUVERT (privilegie, sans
liste d'images, sans capacite retiree) et un pipeline dont les deux attaques
ont REUSSI (le setup l'a mesure, diagnostic dans
/var/tmp/gl-25-diagnostic-depart.txt). Chacun des six tests porte donc sur une
absence, aucun ne peut etre vert au depart :
  1. le runner n'est plus privilegie ;
  2. une liste d'images autorisees existe, laisse passer l'image du pipeline
     legitime et refuse l'image de l'attaque ;
  3. les capacites Linux sont retirees et le gain de privilege interdit ;
  4. apres le durcissement, un pipeline a tourne et le job legitime `tester`
     reussit encore ;
  5. l'attaque sur le privilege est BLOQUEE (le job d'attaque a echoue sur le
     refus du montage) ;
  6. l'attaque par l'image est BLOQUEE (le runner a refuse l'image).

LES TESTS 4 A 6 LISENT LES JOURNAUX DE JOB, pas le statut seul : un job
« failed » peut l'etre pour mille raisons, et seule la phrase du journal dit
qu'il l'a ete pour la bonne. Le dernier pipeline apres le depart est celui qui
compte, ce qui prouve aussi l'ORDRE (le durcissement precede le pipeline), la
ou les verrous de gl-24 ne se datent pas.

CE QUE LES TESTS NE FONT PAS. Ils n'imposent ni les motifs exacts de la liste
(tout motif qui couvre l'image legitime et pas l'attaque convient), ni la facon
d'ecrire le fichier. Ils ne testent pas `allowed_privileged_images` ni les
services. Ils ne rejouent pas un build Docker-in-Docker : un runner durci ne le
permet plus, et le lab le dit.
"""

from __future__ import annotations

import fnmatch
import sys
import tomllib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    api,
    forge_joignable,
    jobs,
    pipelines,
    projet,
)

from conftest import lab_host, message  # noqa: E402

ETAT = "/var/lib/dsoxlab/gl-25"
CONFIG = "/etc/gitlab-runner/config.toml"
RUNNER = "runner-du-lab"
IMAGE_LEGITIME = (
    "alpine:3.24.2@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6"
)
IMAGE_ATTAQUE = (
    "alpine:3.20@sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc"
)
ENCOURS = ("created", "pending", "running", "waiting_for_resource", "preparing")


@pytest.fixture(scope="module")
def host():
    return lab_host(HOTE)


@pytest.fixture(scope="module")
def forge(host):
    assert forge_joignable(host), message(
        en=(
            "GitLab is not answering on gitlab-1.lab yet. It can take several "
            "minutes to start. Check with: curl -I http://gitlab-1.lab/-/readiness"
        ),
        fr=(
            "GitLab ne répond pas encore sur gitlab-1.lab. Son démarrage peut "
            "prendre plusieurs minutes. À vérifier avec : "
            "curl -I http://gitlab-1.lab/-/readiness"
        ),
    )
    return host


@pytest.fixture(scope="module")
def projet_du_lab(forge):
    p = projet(forge)
    assert p is not None, message(
        en="The pipeline-craft project was not found on the lab GitLab instance.",
        fr="Le projet pipeline-craft n'a pas été trouvé sur le GitLab du lab.",
    )
    return p


@pytest.fixture(scope="module")
def docker_runner(host) -> dict:
    """La section [runners.docker] du runner du lab, lue sur la VM."""
    r = host.run(f"cat {CONFIG}")
    assert r.rc == 0 and r.stdout.strip(), message(
        en=f"{CONFIG} cannot be read on the VM. The runner is not set up.",
        fr=f"{CONFIG} est illisible sur la VM. Le runner n'est pas installé.",
    )
    try:
        conf = tomllib.loads(r.stdout)
    except tomllib.TOMLDecodeError as exc:
        pytest.fail(
            message(
                en=(
                    f"{CONFIG} is not valid TOML ({exc}). The runner will not "
                    "start with it: fix the file and restart the runner."
                ),
                fr=(
                    f"{CONFIG} n'est pas du TOML valide ({exc}). Le runner ne "
                    "démarrera pas avec : corrigez le fichier et redémarrez le runner."
                ),
            )
        )
    candidats = [x for x in conf.get("runners", []) if x.get("name") == RUNNER]
    assert candidats, message(
        en=f"The runner {RUNNER} is not in {CONFIG}. Do not rename or remove it.",
        fr=f"Le runner {RUNNER} n'est plus dans {CONFIG}. Ne le renommez pas, ne le retirez pas.",
    )
    return candidats[0].get("docker", {})


def _depart(host) -> int:
    """Le pipeline de depart, pose par le setup. Son absence est une panne du lab."""
    r = host.run(f"cat {ETAT}/depart-pipeline")
    assert r.rc == 0 and r.stdout.strip().isdigit(), message(
        en=(
            f"The setup fact {ETAT}/depart-pipeline is missing or unreadable. The "
            "lab setup did not complete: replay it with dsoxlab run."
        ),
        fr=(
            f"Le fait posé par le setup {ETAT}/depart-pipeline est absent ou "
            "illisible. Le setup du lab n'est pas allé au bout : rejouez-le avec "
            "dsoxlab run."
        ),
    )
    return int(r.stdout.strip())


def _dernier_pipeline_apres_depart(forge, pid: int) -> dict:
    depart = _depart(forge)
    apres = sorted(
        (p for p in pipelines(forge, ref="main", projet_id=pid) if p["id"] > depart),
        key=lambda p: p["id"],
        reverse=True,
    )
    assert apres, message(
        en=(
            "No pipeline has run on main since the lab started. Harden the "
            "runner first, then run a pipeline on main: the attacks replayed "
            "by that pipeline are the proof."
        ),
        fr=(
            "Aucun pipeline n'a tourné sur main depuis le début du lab. "
            "Durcissez d'abord le runner, puis lancez un pipeline sur main : "
            "les attaques que ce pipeline rejoue sont la preuve."
        ),
    )
    dernier = apres[0]
    assert dernier.get("status") not in ENCOURS, message(
        en=f"The latest pipeline is still {dernier.get('status')}. Wait for it, then run the check again.",
        fr=f"Le dernier pipeline est encore {dernier.get('status')}. Attendez-le, puis relancez la vérification.",
    )
    return dernier


def _job(forge, pid: int, dernier: dict, nom: str) -> dict:
    par_nom = {j["name"]: j for j in jobs(forge, dernier["id"], pid)}
    assert nom in par_nom, message(
        en=f"The job {nom} is missing from pipeline {dernier['id']}. Do not edit .gitlab-ci.yml: the attacks are the measure.",
        fr=f"Le job {nom} est absent du pipeline {dernier['id']}. Ne modifiez pas .gitlab-ci.yml : les attaques sont la mesure.",
    )
    return par_nom[nom]


def _journal(forge, pid: int, job: dict) -> str:
    texte = api(forge, f"/projects/{pid}/jobs/{job['id']}/trace", brut=True)
    return texte if isinstance(texte, str) else ""


def test_runner_non_privilegie(docker_runner) -> None:
    """Le runner ne lance plus les jobs en mode privilegie."""
    assert docker_runner.get("privileged", False) is not True, message(
        en=(
            "The runner still has privileged = true. Every job then holds "
            "full root access to the host: a single hostile job escapes the "
            "container. Set privileged = false in [runners.docker]."
        ),
        fr=(
            "Le runner a toujours privileged = true. Chaque job détient alors "
            "un accès root complet à l'hôte : un seul job hostile s'évade du "
            "conteneur. Passez privileged = false dans [runners.docker]."
        ),
    )


def test_images_autorisees_restreintes(docker_runner) -> None:
    """allowed_images existe, laisse passer l'image legitime et refuse celle de l'attaque."""
    liste = docker_runner.get("allowed_images")
    assert isinstance(liste, list) and liste, message(
        en=(
            "allowed_images is absent or empty in [runners.docker]. A missing "
            "key is not neutral: the runner then accepts EVERY image."
        ),
        fr=(
            "allowed_images est absente ou vide dans [runners.docker]. Une clé "
            "absente n'est pas neutre : le runner accepte alors TOUTE image."
        ),
    )
    assert not any(m in ("*", "**", "*/*", "**/*") for m in liste), message(
        en=f"allowed_images = {liste} authorizes every image: a wildcard alone is no list.",
        fr=f"allowed_images = {liste} autorise toute image : un joker seul n'est pas une liste.",
    )
    assert any(fnmatch.fnmatchcase(IMAGE_LEGITIME, m) for m in liste), message(
        en=(
            f"allowed_images = {liste} would refuse the image of the legitimate "
            f"pipeline ({IMAGE_LEGITIME}): hardening must not break the build."
        ),
        fr=(
            f"allowed_images = {liste} refuserait l'image du pipeline légitime "
            f"({IMAGE_LEGITIME}) : le durcissement ne doit pas casser le build."
        ),
    )
    assert not any(fnmatch.fnmatchcase(IMAGE_ATTAQUE, m) for m in liste), message(
        en=f"allowed_images = {liste} still accepts the attack image ({IMAGE_ATTAQUE}).",
        fr=f"allowed_images = {liste} accepte encore l'image de l'attaque ({IMAGE_ATTAQUE}).",
    )


def test_capacites_retirees_et_gain_de_privilege_interdit(docker_runner) -> None:
    """cap_drop contient ALL et security_opt contient no-new-privileges."""
    cap_drop = docker_runner.get("cap_drop") or []
    assert "ALL" in cap_drop, message(
        en=(
            f"cap_drop = {cap_drop}: the container keeps Linux capabilities "
            'it does not need. Drop them all: cap_drop = ["ALL"].'
        ),
        fr=(
            f"cap_drop = {cap_drop} : le conteneur garde des capacités Linux "
            'dont il n\'a pas besoin. Retirez-les toutes : cap_drop = ["ALL"].'
        ),
    )
    options = docker_runner.get("security_opt") or []
    assert "no-new-privileges:true" in options, message(
        en=(
            f"security_opt = {options}: a process in the container can still "
            'gain privileges. Add "no-new-privileges:true".'
        ),
        fr=(
            f"security_opt = {options} : un processus du conteneur peut encore "
            'gagner des privilèges. Ajoutez "no-new-privileges:true".'
        ),
    )


def test_le_job_legitime_passe_encore(forge, projet_du_lab) -> None:
    """Apres le durcissement, un pipeline a tourne et `tester` reussit."""
    pid = projet_du_lab["id"]
    dernier = _dernier_pipeline_apres_depart(forge, pid)
    tester = _job(forge, pid, dernier, "tester")
    assert tester["status"] == "success", message(
        en=(
            f"The legitimate job tester is {tester['status']} after hardening. "
            "A hardened runner that refuses the pipeline is not protection, "
            "it is an outage: read the job log."
        ),
        fr=(
            f"Le job légitime tester est {tester['status']} après le durcissement. "
            "Un runner durci qui refuse le pipeline n'est pas une protection, "
            "c'est une panne : lisez le journal du job."
        ),
    )


def test_attaque_privilege_bloquee(forge, projet_du_lab) -> None:
    """Le job attaque-privilege a echoue parce que le montage est refuse."""
    pid = projet_du_lab["id"]
    dernier = _dernier_pipeline_apres_depart(forge, pid)
    job = _job(forge, pid, dernier, "attaque-privilege")
    journal = _journal(forge, pid, job)
    assert "ATTAQUE-REUSSIE" not in journal, message(
        en="The privilege attack still succeeds: the container can mount a filesystem.",
        fr="L'attaque sur le privilège réussit encore : le conteneur peut monter un système de fichiers.",
    )
    assert job["status"] == "failed" and "ATTAQUE-BLOQUEE" in journal, message(
        en=(
            f"The job attaque-privilege is {job['status']} but its log does not "
            "show ATTAQUE-BLOQUEE. A blocked attack is a job that failed on the "
            "refused mount, not a job that never ran."
        ),
        fr=(
            f"Le job attaque-privilege est {job['status']} mais son journal ne "
            "montre pas ATTAQUE-BLOQUEE. Une attaque bloquée est un job qui a "
            "échoué sur le montage refusé, pas un job qui n'a jamais tourné."
        ),
    )


def test_attaque_image_bloquee(forge, projet_du_lab) -> None:
    """Le job attaque-image a ete refuse par le runner : l'image n'est pas autorisee."""
    pid = projet_du_lab["id"]
    dernier = _dernier_pipeline_apres_depart(forge, pid)
    job = _job(forge, pid, dernier, "attaque-image")
    journal = _journal(forge, pid, job)
    assert "ATTAQUE-REUSSIE" not in journal, message(
        en="The image attack still succeeds: the runner ran an image nobody validated.",
        fr="L'attaque par l'image réussit encore : le runner a exécuté une image que personne n'a validée.",
    )
    assert job["status"] == "failed" and "allowed images" in journal, message(
        en=(
            f"The job attaque-image is {job['status']} but the runner did not "
            "refuse the image (expected: not present on the list of allowed "
            "images). Read the job log."
        ),
        fr=(
            f"Le job attaque-image est {job['status']} mais le runner n'a pas "
            "refusé l'image (attendu : image absente de la liste des images "
            "autorisées). Lisez le journal du job."
        ),
    )
