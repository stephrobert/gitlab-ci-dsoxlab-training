"""Tests du lab gl-11-diagnostiquer-un-job-bloque.

DEUX PANNES, ET AUCUNE NE PRODUIT DE MESSAGE. C'est ce qui fait de ce lab un
lab de diagnostic et non de correction :

- le `workflow:` n'accepte qu'une provenance, `$CI_COMMIT_TAG`. Un push sur la
  branche par defaut ne cree donc AUCUN pipeline. Rien n'est rouge : il n'y a
  rien, et un onglet vide ne dit pas pourquoi il est vide ;
- un job exige un runner porteur d'un tag que personne n'a. Il reste alors en
  attente indefiniment, sans jamais echouer : le pipeline n'avance plus et ne
  se plaint pas.

Les deux tests mesurent donc ce que l'etat de depart ne porte pas :

- un pipeline EXISTE sur la branche par defaut, ce qui prouve que la premiere
  panne est levee ;
- aucun job n'est reste EN ATTENTE, et le lint a reussi, ce qui prouve que la
  seconde l'est aussi. Ce test porte en plus l'exigence qu'aucun job n'ait
  echoue : elle serait vraie sur un etat sans pipeline, donc elle ne peut pas
  faire un test a elle seule.

UN STATUT A NE PAS CONFONDRE AVEC UNE PANNE : `manual`. Un job en attente de
decision humaine est un job sain, et le pipeline en porte un a ce rang du
parcours. Les tests l'excluent explicitement de ce qu'ils comptent comme
bloque.
"""

from __future__ import annotations

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

# Les statuts qui disent « ce job n'a pas pu demarrer ». `manual` n'en fait
# PAS partie : un job qui attend une decision humaine est un job sain.
BLOQUES = ("pending", "created", "waiting_for_resource", "preparing")


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


def test_un_pipeline_nait_enfin_sur_la_branche_par_defaut(forge, projet_du_lab):
    """La premiere panne : un `workflow:` qui refusait le push.

    Un onglet Pipelines vide ne dit pas pourquoi il est vide. C'est la panne la
    plus silencieuse de GitLab CI : rien n'a echoue, rien n'a ete ignore, rien
    n'a ete cree.
    """
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en=(
            "No pipeline exists on the default branch. Nothing failed and "
            "nothing was skipped: nothing was created. Look at what the "
            "top-level `workflow:` block accepts as a source."
        ),
        fr=(
            "Aucun pipeline n'existe sur la branche par défaut. Rien n'a "
            "échoué et rien n'a été ignoré : rien n'a été créé. Regardez ce "
            "que le bloc `workflow:` de premier niveau accepte comme source."
        ),
    )


def test_aucun_job_ne_reste_en_attente(forge, projet_du_lab):
    """La seconde panne : un tag de runner que personne ne porte.

    Un job qui exige un tag introuvable reste en attente SANS ECHOUER. Le
    pipeline n'avance plus et ne se plaint pas : c'est au lecteur de remarquer
    que rien ne bouge.

    Ce test porte aussi l'exigence qu'aucun job n'ait echoue, et ce n'est pas
    de la paresse : sur l'etat de depart, ou aucun pipeline n'existe, cette
    exigence serait vraie, et un test separe passerait avant tout travail.
    """
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline exists on the default branch yet.",
        fr="Aucun pipeline n'existe encore sur la branche par défaut.",
    )
    tous = jobs(forge, dernier["id"], projet_du_lab["id"])
    assert tous, message(
        en="The latest pipeline has no job at all: GitLab refused its configuration.",
        fr="Le dernier pipeline ne contient aucun job : GitLab a refusé sa configuration.",
    )

    bloques = [
        f"{j.get('name')} ({j.get('status')})" for j in tous
        if j.get("status") in BLOQUES
    ]
    assert not bloques, message(
        en=(
            f"These jobs never started: {bloques}. A job that requires a tag no "
            "runner carries waits forever, without ever failing. Check the "
            "runner's tags against what the job asks for."
        ),
        fr=(
            f"Ces jobs n'ont jamais démarré : {bloques}. Un job qui exige un "
            "tag qu'aucun runner ne porte attend indéfiniment, sans jamais "
            "échouer. Comparez les tags du runner à ce que le job demande."
        ),
    )

    echoues = [
        j.get("name") for j in tous
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=f"These jobs failed in the latest pipeline: {echoues}.",
        fr=f"Ces jobs ont échoué dans le dernier pipeline : {echoues}.",
    )

    # Le lint est le job que la seconde panne retenait : le voir REUSSIR ferme
    # le diagnostic, la ou l'absence de blocage pourrait aussi venir d'un job
    # simplement ecarte par une regle.
    traces = ""
    for j in tous:
        if j.get("status") != "success":
            continue
        brut = api(
            forge,
            f"/projects/{projet_du_lab['id']}/jobs/{j['id']}/trace",
            brut=True,
        )
        if brut:
            traces += brut.lower()
    assert "ruff" in traces, message(
        en=(
            "No successful job's log shows the linter running. A job removed "
            "from the pipeline is no longer blocked, but it is not fixed "
            "either."
        ),
        fr=(
            "Aucun journal de job réussi ne montre le linter tourner. Un job "
            "retiré du pipeline n'est plus bloqué, mais il n'est pas réparé "
            "pour autant."
        ),
    )
