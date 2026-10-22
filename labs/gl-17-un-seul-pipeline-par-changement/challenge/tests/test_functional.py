"""Tests du lab gl-17-un-seul-pipeline-par-changement.

LE LAB LE PLUS DIRECTEMENT MESURABLE DE LA SERIE : on compte les pipelines sur
un meme commit. Deux, c'est le defaut ; un, c'est le travail fait.

Les deux tests portent sur ce que le serveur a produit :

- UNE DEMANDE DE FUSION EST OUVERTE, avec une branche source distincte de la
  branche par defaut. Sans elle, le doublon ne peut pas se produire, donc rien
  ne peut etre mesure : c'est un geste du lab, pas une formalite ;
- SUR LE DERNIER COMMIT DE CETTE BRANCHE, UN SEUL PIPELINE, et il vient de
  l'evenement de demande de fusion. C'est la mesure du lab.

POURQUOI CE SENS ET PAS L'AUTRE. On pourrait croire qu'il suffit de garder le
pipeline de branche et de refuser celui de la demande de fusion. Ce serait
perdre ce que le second sait faire : il connait la cible de la fusion, donc il
peut comparer, et c'est lui qui s'affiche dans la demande. Le lab demande donc
un pipeline de DEMANDE DE FUSION, pas n'importe lequel des deux.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    api,
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
def projet_du_lab(forge):
    p = projet(forge)
    assert p is not None, message(
        en="The pipeline-craft project was not found on the lab GitLab instance.",
        fr="Le projet pipeline-craft n'a pas été trouvé sur le GitLab du lab.",
    )
    return p


@pytest.fixture(scope="module")
def demande(forge, projet_du_lab):
    """La demande de fusion ouverte sur laquelle le lab se mesure."""
    ouvertes = api(
        forge,
        f"/projects/{projet_du_lab['id']}/merge_requests",
        "state=opened&per_page=20",
    )
    return ouvertes if isinstance(ouvertes, list) else []


def test_une_demande_de_fusion_est_ouverte(projet_du_lab, demande):
    """Sans demande de fusion, le doublon ne peut pas se produire.

    Ce n'est pas une formalite : c'est la situation que le lab corrige. Un
    pipeline de branche et un pipeline de demande de fusion ne se recouvrent
    que lorsque les deux existent.
    """
    assert demande, message(
        en=(
            "No open merge request on the project. The duplicate this lab fixes "
            "only happens when a branch carries an open merge request: push a "
            "branch and open one."
        ),
        fr=(
            "Aucune demande de fusion ouverte sur le projet. Le doublon que ce "
            "lab corrige n'arrive que lorsqu'une branche porte une demande de "
            "fusion ouverte : poussez une branche et ouvrez-en une."
        ),
    )

    defaut = projet_du_lab.get("default_branch") or "main"
    distinctes = [m for m in demande if m.get("source_branch") != defaut]
    assert distinctes, message(
        en=(
            f"The open merge request(s) start from '{defaut}', the default "
            "branch. A merge request compares two branches: its source has to "
            "be another one."
        ),
        fr=(
            f"La ou les demandes de fusion ouvertes partent de « {defaut} », la "
            "branche par défaut. Une demande de fusion compare deux branches : "
            "sa source doit en être une autre."
        ),
    )


def test_un_seul_pipeline_par_commit_de_la_branche(forge, projet_du_lab, demande):
    """LA MESURE DU LAB : deux pipelines pour un commit, c'est le defaut.

    On compte les pipelines du DERNIER COMMIT de la branche source. Deux
    signifie que la branche et la demande de fusion en declenchent chacune un ;
    un seul, de source `merge_request_event`, signifie que le recouvrement est
    ferme.

    Ce test porte aussi le garde-fou habituel : aucun job en echec dans le
    pipeline retenu.
    """
    defaut = projet_du_lab.get("default_branch") or "main"
    cibles = [m for m in demande if m.get("source_branch") != defaut]
    assert cibles, message(
        en="No merge request from a branch other than the default one.",
        fr="Aucune demande de fusion partant d'une autre branche que la branche par défaut.",
    )

    mr = cibles[0]
    sha = mr.get("sha")
    assert sha, message(
        en="The merge request carries no commit identifier.",
        fr="La demande de fusion ne porte aucun identifiant de commit.",
    )

    tous = api(
        forge,
        f"/projects/{projet_du_lab['id']}/pipelines",
        f"sha={sha}&per_page=20",
    )
    assert isinstance(tous, list), message(
        en="The project's pipelines could not be read.",
        fr="Les pipelines du projet n'ont pas pu être lus.",
    )

    # Les pipelines de demande de fusion portent la source
    # `merge_request_event` ; ceux de branche, `push`.
    par_source: dict[str, int] = {}
    for p in tous:
        s = p.get("source") or "inconnue"
        par_source[s] = par_source.get(s, 0) + 1

    assert tous, message(
        en=(
            f"No pipeline ran on the merge request's commit ({sha[:8]}). The "
            "`workflow:` block may now refuse every source: a rule that says "
            "`when: never` too broadly stops everything."
        ),
        fr=(
            f"Aucun pipeline n'a tourné sur le commit de la demande de fusion "
            f"({sha[:8]}). Le bloc `workflow:` refuse peut-être désormais "
            "toutes les sources : une règle `when: never` trop large arrête "
            "tout."
        ),
    )

    assert len(tous) == 1, message(
        en=(
            f"{len(tous)} pipelines ran on the same commit ({sha[:8]}): "
            f"{par_source}. The machine does everything twice, and the merge "
            "request shows two results without saying which one counts."
        ),
        fr=(
            f"{len(tous)} pipelines ont tourné sur le même commit "
            f"({sha[:8]}) : {par_source}. La machine fait tout deux fois, et la "
            "demande de fusion affiche deux résultats sans dire lequel compte."
        ),
    )

    retenu = tous[0]
    assert retenu.get("source") == "merge_request_event", message(
        en=(
            f"The only pipeline on that commit comes from "
            f"'{retenu.get('source')}', not from the merge request event. "
            "Keeping the branch pipeline instead loses what the merge request "
            "one knows: the target of the merge, and the place where the "
            "result is shown."
        ),
        fr=(
            f"Le seul pipeline de ce commit vient de "
            f"« {retenu.get('source')} », pas de l'événement de demande de "
            "fusion. Garder le pipeline de branche à sa place perd ce que "
            "l'autre sait : la cible de la fusion, et l'endroit où le résultat "
            "s'affiche."
        ),
    )

    echoues = [
        j.get("name")
        for j in jobs(forge, retenu["id"], projet_du_lab["id"])
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=f"These jobs failed in the merge request pipeline: {echoues}.",
        fr=f"Ces jobs ont échoué dans le pipeline de la demande de fusion : {echoues}.",
    )
