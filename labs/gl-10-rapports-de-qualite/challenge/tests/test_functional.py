"""Tests du lab gl-10-rapports-de-qualite.

CE QUE L'ETAT DE DEPART PORTE DEJA, et qu'aucun test ne mesure donc seul : le
rapport JUnit, acquis du lab 04, remplit l'onglet Tests du pipeline. Un test
qui le verifierait passerait avant tout travail.

CE QUE LE LAB AJOUTE, et que les deux tests mesurent :

- la COUVERTURE, remontee au pipeline. GitLab ne la devine pas : le job doit
  l'imprimer, et une expression reguliere `coverage:` doit l'y pecher. Le
  chiffre apparait alors sur le pipeline, sur le job, et dans la demande de
  fusion ;
- un RAPPORT DE COUVERTURE exploitable, declare en artefact de type
  `coverage_report`. C'est lui qui fait apparaitre la couverture LIGNE PAR
  LIGNE dans le diff d'une demande de fusion. Sans lui, on a un pourcentage
  global et rien pour savoir quelles lignes ne sont pas testees.

La difference entre les deux est tout le sujet : un pourcentage dit ou on en
est, un rapport dit quoi faire.
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
    # Le detail du pipeline porte son champ `coverage`, que la liste ne rend
    # pas toujours : on le relit par son identifiant.
    detail = api(forge, f"/projects/{p['id']}/pipelines/{dernier['id']}")
    return {
        "projet": p,
        "pipeline": detail if isinstance(detail, dict) else dernier,
        "jobs": jobs(forge, dernier["id"], p["id"]),
    }


def _nombre(valeur) -> float | None:
    """Lit une couverture, que GitLab rende un nombre ou une chaine.

    Le champ vaut `null` quand rien ne l'a renseigne, `"87.5"` ou `87.5` sinon.
    Un test qui comparerait directement a zero prendrait `null` pour une
    couverture nulle, ce qui n'est pas la meme chose : l'un dit « pas mesure »,
    l'autre « mesure a zero ».
    """
    if valeur is None:
        return None
    if isinstance(valeur, (int, float)):
        return float(valeur)
    trouve = re.search(r"\d+(?:[.,]\d+)?", str(valeur))
    return float(trouve.group().replace(",", ".")) if trouve else None


def test_la_couverture_est_remontee_au_pipeline(forge, contexte):
    """GitLab ne devine pas la couverture : il la peche dans le journal.

    Le chiffre doit apparaitre sur le pipeline OU sur un job. Les deux sont
    acceptes, parce que GitLab remonte au pipeline la couverture des jobs et
    que la version de l'instance decide de ce qui est agrege.
    """
    du_pipeline = _nombre(contexte["pipeline"].get("coverage"))
    des_jobs = []
    for j in contexte["jobs"]:
        detail = api(forge, f"/projects/{contexte['projet']['id']}/jobs/{j['id']}")
        if isinstance(detail, dict):
            n = _nombre(detail.get("coverage"))
            if n is not None:
                des_jobs.append((j.get("name"), n))

    assert du_pipeline is not None or des_jobs, message(
        en=(
            "No coverage figure reached GitLab, neither on the pipeline nor on "
            "any job. GitLab does not compute coverage: the job must print it, "
            "and a `coverage:` regular expression must fish it out of the log."
        ),
        fr=(
            "Aucun chiffre de couverture n'est remonté à GitLab, ni sur le "
            "pipeline, ni sur un job. GitLab ne calcule pas la couverture : le "
            "job doit l'imprimer, et une expression régulière `coverage:` doit "
            "aller la pêcher dans le journal."
        ),
    )

    valeurs = [v for _, v in des_jobs] + ([du_pipeline] if du_pipeline is not None else [])
    assert any(v > 0 for v in valeurs), message(
        en=(
            f"The coverage reported is {valeurs}: zero everywhere. A test suite "
            "that covers nothing is either not running, or not watching the "
            "right package."
        ),
        fr=(
            f"La couverture remontée vaut {valeurs} : zéro partout. Une suite "
            "de tests qui ne couvre rien, ou ne tourne pas, ou ne regarde pas "
            "le bon paquet."
        ),
    )


def test_un_rapport_de_couverture_est_publie(forge, contexte):
    """Un pourcentage dit ou on en est ; un rapport dit quoi faire.

    Declare en `artifacts: reports: coverage_report:`, le rapport fait
    apparaitre la couverture LIGNE PAR LIGNE dans le diff d'une demande de
    fusion. Il se reconnait au `file_type` de l'artefact, que l'API expose.

    CE TEST PORTE AUSSI L'EXIGENCE DE NON-REGRESSION, et ce n'est pas de la
    paresse : le rapport JUnit et la sante du pipeline sont vrais DES L'ETAT DE
    DEPART, donc des tests separes passeraient avant tout travail. Ils
    s'ajoutent ici, au test qui mesure le travail reel.
    """
    types = []
    for j in contexte["jobs"]:
        detail = api(forge, f"/projects/{contexte['projet']['id']}/jobs/{j['id']}")
        if isinstance(detail, dict):
            for a in detail.get("artifacts") or []:
                if a.get("file_type"):
                    types.append(a["file_type"])

    attendus = {"cobertura", "coverage_report"}
    assert attendus & set(types), message(
        en=(
            f"No coverage report was published. Artifact types found: "
            f"{sorted(set(types))}. A percentage says where you stand; a "
            "report says what to do, line by line in the merge request."
        ),
        fr=(
            f"Aucun rapport de couverture n'est publié. Types d'artefacts "
            f"trouvés : {sorted(set(types))}. Un pourcentage dit où l'on en "
            "est ; un rapport dit quoi faire, ligne par ligne dans la demande "
            "de fusion."
        ),
    )

    # Non-regression : l'acquis du lab 04 tient toujours.
    rapport = api(
        forge,
        f"/projects/{contexte['projet']['id']}/pipelines/{contexte['pipeline']['id']}/test_report",
    )
    total = rapport.get("total_count") if isinstance(rapport, dict) else 0
    assert (total or 0) > 0, message(
        en=(
            "GitLab's test report is now empty: the JUnit report of the "
            "previous lab was lost along the way."
        ),
        fr=(
            "Le rapport de tests de GitLab est maintenant vide : le rapport "
            "JUnit du lab précédent a été perdu en route."
        ),
    )

    echoues = [
        j.get("name") for j in contexte["jobs"]
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=(
            f"These jobs failed in the latest pipeline: {echoues} (pipeline "
            f"status '{contexte['pipeline'].get('status')}')."
        ),
        fr=(
            f"Ces jobs ont échoué dans le dernier pipeline : {echoues} (statut "
            f"du pipeline « {contexte['pipeline'].get('status')} »)."
        ),
    )
