"""Tests du lab gl-15-une-matrice-de-tests.

UNE MATRICE SE MESURE TRES BIEN, et c'est un soulagement apres deux labs de
factorisation dont l'effet etait invisible. GitLab instancie un job par
combinaison, les nomme avec les valeurs qui les distinguent, et les fait
tourner en parallele : tout cela se lit dans l'API.

Les deux tests portent sur ce que le serveur a produit :

- PLUSIEURS INSTANCES du job de tests ont reussi, et elles sont distinctes.
  Une matrice qui ne produirait qu'un job ne serait pas une matrice ;
- LES COMBINAISONS CHANGENT VRAIMENT QUELQUE CHOSE. C'est la moitie qui compte
  le plus : une matrice peut declarer quatre combinaisons et lancer quatre fois
  exactement le meme travail. On verifie donc que les jobs ont tire des IMAGES
  DIFFERENTES, ce que leur journal inscrit.

Le second test porte aussi les garde-fous habituels, vrais des l'etat de
depart : aucun job en echec, et la couverture remonte encore.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    api,
    dernier_pipeline,
    forge_joignable,
    jobs,
    projet,
)

from conftest import lab_host, message  # noqa: E402


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
def contexte(forge):
    p = projet(forge)
    assert p is not None, message(
        en="The pipeline-craft project was not found on the lab GitLab instance.",
        fr="Le projet pipeline-craft n'a pas été trouvé sur le GitLab du lab.",
    )
    dernier = dernier_pipeline(forge, p.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut.",
    )
    return {"projet": p, "pipeline": dernier, "jobs": jobs(forge, dernier["id"], p["id"])}


def _instances_de_matrice(jobs_du_pipeline: list) -> list[dict]:
    """Les jobs nes d'une matrice, reconnus a leur nom.

    GitLab nomme une instance de matrice `job: [valeur, valeur]`. Le crochet
    est le signe le plus fiable : il n'apparait pas dans un nom de job
    ordinaire, et il ne depend pas du nom que l'apprenant a choisi.
    """
    return [j for j in jobs_du_pipeline if "[" in (j.get("name") or "")]


def test_la_matrice_a_produit_plusieurs_jobs(contexte):
    """Une matrice qui ne produit qu'un job n'est pas une matrice."""
    instances = _instances_de_matrice(contexte["jobs"])
    noms = sorted(j.get("name") for j in instances)
    assert len(instances) >= 3, message(
        en=(
            f"The pipeline carries {len(instances)} matrix job(s): {noms}. A "
            "matrix instantiates one job per combination, and GitLab names "
            "them `job: [value, value]`."
        ),
        fr=(
            f"Le pipeline porte {len(instances)} job(s) de matrice : {noms}. "
            "Une matrice instancie un job par combinaison, et GitLab les nomme "
            "`job: [valeur, valeur]`."
        ),
    )

    reussies = [j for j in instances if j.get("status") == "success"]
    assert len(reussies) >= 3, message(
        en=(
            f"Only {len(reussies)} matrix job(s) out of {len(instances)} "
            "succeeded. A combination that fails is a combination worth "
            "knowing about: that is the point of the matrix."
        ),
        fr=(
            f"Seulement {len(reussies)} job(s) de matrice sur {len(instances)} "
            "ont réussi. Une combinaison qui échoue est une combinaison qu'il "
            "fallait connaître : c'est tout l'intérêt de la matrice."
        ),
    )


def test_les_combinaisons_changent_vraiment_quelque_chose(forge, contexte):
    """LA MOITIE QUI COMPTE LE PLUS : une matrice peut ne rien faire varier.

    Declarer quatre combinaisons et lancer quatre fois le meme travail donne un
    pipeline quatre fois plus lent sans rien apprendre de plus. On verifie donc
    que les jobs ont tire des IMAGES DIFFERENTES, ce que le runner inscrit dans
    chaque journal (« Using docker image … for python:3.12-slim »).

    Ce test porte aussi les garde-fous : aucun job en echec, et la couverture
    remonte encore. Vrais des l'etat de depart, ils ne peuvent pas faire des
    tests a eux seuls.
    """
    instances = _instances_de_matrice(contexte["jobs"])
    assert instances, message(
        en="No matrix job in the pipeline: nothing to compare.",
        fr="Aucun job de matrice dans le pipeline : il n'y a rien à comparer.",
    )

    images: dict[str, set[str]] = {}
    for j in instances:
        brut = api(
            forge,
            f"/projects/{contexte['projet']['id']}/jobs/{j['id']}/trace",
            brut=True,
        )
        trouvees = set(re.findall(r"for (python:[\w.-]+)", (brut or "").lower()))
        images[j.get("name")] = trouvees

    toutes = set().union(*images.values()) if images else set()
    assert len(toutes) >= 2, message(
        en=(
            f"All matrix jobs pulled the same image(s): {sorted(toutes)}. A "
            "matrix that varies nothing runs the same work several times: it "
            "costs time and teaches nothing. Per job: "
            + "; ".join(f"{n} -> {sorted(v)}" for n, v in images.items())
        ),
        fr=(
            f"Tous les jobs de la matrice ont tiré la ou les mêmes images : "
            f"{sorted(toutes)}. Une matrice qui ne fait rien varier relance le "
            "même travail plusieurs fois : elle coûte du temps et n'apprend "
            "rien. Par job : "
            + " ; ".join(f"{n} -> {sorted(v)}" for n, v in images.items())
        ),
    )

    # --- Garde-fous, vrais des l'etat de depart ---------------------------
    echoues = [
        j.get("name") for j in contexte["jobs"]
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=f"These jobs failed in the latest pipeline: {echoues}.",
        fr=f"Ces jobs ont échoué dans le dernier pipeline : {echoues}.",
    )

    detail = api(
        forge,
        f"/projects/{contexte['projet']['id']}/pipelines/{contexte['pipeline']['id']}",
    )
    couverture = detail.get("coverage") if isinstance(detail, dict) else None
    des_jobs = [
        d.get("coverage")
        for j in contexte["jobs"]
        if j.get("status") == "success"
        and isinstance(
            d := api(forge, f"/projects/{contexte['projet']['id']}/jobs/{j['id']}"), dict
        )
        and d.get("coverage") is not None
    ]
    assert couverture is not None or des_jobs, message(
        en=(
            "No coverage figure reaches GitLab any more. `coverage:` belongs to "
            "the job, and a matrix instantiates the job: each instance reports "
            "its own, GitLab averaging them."
        ),
        fr=(
            "Aucun chiffre de couverture ne remonte plus à GitLab. `coverage:` "
            "appartient au job, et une matrice instancie le job : chaque "
            "instance remonte la sienne, GitLab en faisant la moyenne."
        ),
    )
