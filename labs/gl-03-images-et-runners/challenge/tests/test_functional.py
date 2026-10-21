"""Tests du lab gl-03-images-et-runners.

CE QUE CE LAB NOTE, ET POURQUOI C'EST DELICAT. La mission demande deux choses
de nature differente : faire fonctionner le job de construction, ce qui est
objectif, et alleger les images, ce qui ne l'est pas. Un test qui exigerait
litteralement `slim` refuserait `python:3.12-alpine`, qui est un choix aussi
defendable, et noterait alors la conformite a notre corrige plutot que la
comprehension.

La ligne retenue, lue dans les JOURNAUX des jobs, ou GitLab Runner inscrit
l'image qu'il a tiree (« Using docker image … for python:3.12-slim@sha256:… ») :

- le pipeline est vert ;
- le job qui construit l'image a REUSSI son `docker build`, ce qui est
  impossible depuis une image Python sans client Docker ;
- un service Docker a bien ete demarre pour ce job ;
- les jobs de lint et de test ne tournent PLUS sur `python:3.12` nu. On
  n'impose pas quelle image les remplace.

Les traces sont la seule source : ni le nom des jobs, ni le contenu du
`.gitlab-ci.yml` n'entrent dans la note.
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
def pipeline(forge):
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
    return {"projet": p, "pipeline": dernier}


@pytest.fixture(scope="module")
def journaux(forge, pipeline):
    """Le journal de CHAQUE job, indexe par son identifiant.

    Un seul relevé pour les quatre tests : chaque journal coute un appel a
    l'API depuis la VM, et les repeter rendrait la notation lente sans rien
    mesurer de plus.
    """
    tous = jobs(forge, pipeline["pipeline"]["id"], pipeline["projet"]["id"])
    lus = {}
    for j in tous:
        brut = api(
            forge,
            f"/projects/{pipeline['projet']['id']}/jobs/{j['id']}/trace",
            brut=True,
        )
        lus[j["id"]] = {"job": j, "trace": (brut or "").lower()}
    return lus


def test_le_pipeline_est_vert(pipeline):
    statut = pipeline["pipeline"].get("status")
    assert statut == "success", message(
        en=f"The latest pipeline on the default branch is '{statut}', not 'success'.",
        fr=f"Le dernier pipeline de la branche par défaut est « {statut} », pas « success ».",
    )


def test_l_image_est_construite_pour_de_vrai(journaux):
    """Le `docker build` doit avoir ABOUTI dans un job reussi.

    Depuis `python:3.12`, la commande echoue sur « docker: command not found » :
    l'image n'embarque aucun client Docker. C'est le defaut de depart, et sa
    correction ne se devine pas depuis le fichier, elle se lit dans le journal.
    """
    reussis = [e for e in journaux.values() if e["job"].get("status") == "success"]
    construits = [
        e for e in reussis
        if "docker build" in e["trace"] and "command not found" not in e["trace"]
    ]
    assert construits, message(
        en=(
            "No successful job carries a completed `docker build`. A Python "
            "image has no Docker client: the command fails on "
            "'docker: command not found'."
        ),
        fr=(
            "Aucun job réussi ne porte un `docker build` mené à bien. Une image "
            "Python n'embarque pas de client Docker : la commande échoue sur "
            "« docker: command not found »."
        ),
    )


def test_un_service_docker_a_ete_demarre(journaux):
    """Construire une image demande un demon, fourni par un service du job.

    GitLab Runner inscrit dans le journal les services qu'il demarre. Sans
    service, un `docker build` ne peut joindre aucun demon, et l'erreur parle
    de socket, pas d'image.
    """
    # LE MOTIF DOIT ETRE SPECIFIQUE AU DEMARRAGE D'UN SERVICE, et la premiere
    # version ne l'etait pas : elle acceptait « docker: », qui apparait aussi
    # dans « docker: command not found », c'est-a-dire dans l'ECHEC de depart.
    # Le test passait donc avant tout travail, ce que `valider-labs.py` a
    # refuse : un test vert sur l'etat de depart n'est pas un test.
    #
    # GitLab Runner n'ecrit ces deux lignes que lorsqu'un `services:` est
    # declare sur le job.
    traces = "\n".join(e["trace"] for e in journaux.values())
    motifs = ("starting service", "waiting for services")
    assert any(m in traces for m in motifs), message(
        en=(
            "No job log mentions a Docker service. Building an image needs a "
            "daemon, provided by a `services:` entry on that job."
        ),
        fr=(
            "Aucun journal ne mentionne de service Docker. Construire une image "
            "exige un démon, fourni par une entrée `services:` sur ce job."
        ),
    )


def test_les_images_lourdes_ont_ete_remplacees(journaux):
    """Plus aucun job ne doit tirer `python:3.12` NU.

    On ne dicte pas l'image de remplacement : `-slim`, `-alpine` ou une autre
    base legere conviennent. Ce test refuse seulement l'image complete du
    depart, reconnue dans la ligne « Using docker image … for python:3.12 »
    sans suffixe.
    """
    # `python:3.12` suivi d'un digest ou d'une fin de champ, mais PAS de `-slim`
    # ni d'un autre suffixe de variante.
    lourde = re.compile(r"for python:3\.12(?![\w.-])")
    coupables = [
        e["job"].get("name")
        for e in journaux.values()
        if lourde.search(e["trace"])
    ]
    assert not coupables, message(
        en=(
            f"These jobs still pull the full `python:3.12` image: {coupables}. "
            "A lighter variant pulls far less for the same work."
        ),
        fr=(
            f"Ces jobs tirent encore l'image complète `python:3.12` : "
            f"{coupables}. Une variante allégée télécharge bien moins pour le "
            "même travail."
        ),
    )
