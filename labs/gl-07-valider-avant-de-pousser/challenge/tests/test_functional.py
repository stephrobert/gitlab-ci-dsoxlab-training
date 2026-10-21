"""Tests du lab gl-07-valider-avant-de-pousser.

CE QUE CE LAB NE PEUT PAS MESURER, ET IL FAUT LE DIRE. Son sujet est une
METHODE : valider la configuration avant de pousser, au lieu de pousser pour
voir. Or l'etat final d'un apprenant methodique et celui d'un apprenant qui a
tatonne sont identiques. Aucun test ne peut donc noter la methode, et aucun
n'essaie : les tests notent l'etat, et le scenario porte la methode.

LES TROIS DEFAUTS DE DEPART, ET POURQUOI ILS NE SE VALENT PAS :

  - `stage: tests` nomme un stage absent de la liste. GitLab REFUSE toute la
    configuration : le pipeline apparait rouge SANS AUCUN job ;
  - `needs: [build-image]` nomme un job qui n'existe pas. Ce defaut est
    INVISIBLE tant que le premier est la, puisque rien n'est evalue ;
  - `changes: [app/***]` ecrit trois etoiles. GitLab l'ACCEPTE : ce defaut ne
    se voit ni au refus, ni a l'execution. Seule une relecture, ou un controle,
    le trouve.

Le troisieme est celui qui justifie le lab : un fichier que GitLab accepte
n'est pas pour autant un fichier juste.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    dernier_pipeline,
    forge_joignable,
    jobs,
    lint_configuration,
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
def rapport_lint(forge, projet_du_lab):
    rapport = lint_configuration(forge, projet_du_lab["id"])
    assert rapport is not None, message(
        en="GitLab's CI linter did not answer; the configuration could not be checked.",
        fr="Le linter CI de GitLab n'a pas répondu : la configuration n'a pas pu être vérifiée.",
    )
    return rapport


def test_la_configuration_est_acceptee(rapport_lint):
    """Ferme les deux premiers defauts, ceux que GitLab sait refuser."""
    erreurs = rapport_lint.get("errors") or []
    assert rapport_lint.get("valid") is True, message(
        en=f"GitLab still refuses the configuration: {erreurs}",
        fr=f"GitLab refuse encore la configuration : {erreurs}",
    )


def test_aucun_motif_a_trois_etoiles_ne_subsiste(rapport_lint):
    """Le defaut que GitLab ACCEPTE, et donc que rien ne signale.

    `app/***` n'est pas une erreur de syntaxe : c'est un motif qui ne
    correspond pas a ce que son auteur croyait. Le lab le fait trouver par la
    relecture, et ce test le mesure dans la configuration que GitLab a
    comprise, faute d'effet observable a l'execution.
    """
    fusionne = rapport_lint.get("merged_yaml") or ""
    assert fusionne, message(
        en="GitLab did not return the merged configuration.",
        fr="GitLab n'a pas rendu la configuration fusionnée.",
    )
    assert "***" not in fusionne, message(
        en=(
            "A three-star pattern is still in the configuration. GitLab "
            "accepts it without complaint, which is exactly why it survives: "
            "the pattern for 'every file under a directory' is `dir/**/*`."
        ),
        fr=(
            "Un motif à trois étoiles est encore dans la configuration. GitLab "
            "l'accepte sans broncher, et c'est précisément pour cela qu'il "
            "survit : le motif pour « tout fichier sous un répertoire » est "
            "`dossier/**/*`."
        ),
    )


def test_le_job_de_tests_a_tourne_et_reussi(forge, projet_du_lab):
    """La preuve que le stage et le `needs` sont corriges.

    Un job qui vise un stage inexistant ne tourne jamais ; un job qui depend
    d'un job absent non plus. Le voir REUSSIR ferme les deux defauts d'un
    coup, et le fait dans l'etat laisse sur la forge, non dans le fichier.
    """
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch since your corrections.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut depuis vos corrections.",
    )
    tous = jobs(forge, dernier["id"], projet_du_lab["id"])
    assert tous, message(
        en=(
            "The latest pipeline has no job at all, which means GitLab refused "
            "the configuration before creating any."
        ),
        fr=(
            "Le dernier pipeline ne contient aucun job : GitLab a donc refusé "
            "la configuration avant d'en créer un seul."
        ),
    )
    reussis = [j for j in tous if j.get("status") == "success"]
    assert len(reussis) >= 2, message(
        en=(
            f"Only {len(reussis)} job(s) succeeded in the latest pipeline. The "
            "lint and the tests should both have run."
        ),
        fr=(
            f"Seulement {len(reussis)} job(s) ont réussi dans le dernier "
            "pipeline. Le lint et les tests devraient tous deux avoir tourné."
        ),
    )


def test_aucun_job_n_a_echoue(forge, projet_du_lab):
    """La sante du pipeline, mesuree sur ses JOBS et non sur son statut.

    A ce rang du parcours, le pipeline porte deja un deploiement de production
    en `when: manual` (acquis du lab 06). Mesure du 2026-10-22 : un pipeline
    dont un job manuel attend porte alors le statut **`manual`**, pas
    `success`, et exiger `success` ferait echouer un travail juste. On mesure
    donc ce qui compte : aucun job en echec.
    """
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch since your corrections.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut depuis vos corrections.",
    )
    statut = dernier.get("status")
    tous = jobs(forge, dernier["id"], projet_du_lab["id"])
    echoues = [
        j.get("name") for j in tous
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=(
            f"These jobs failed in the latest pipeline: {echoues} (pipeline "
            f"status '{statut}')."
        ),
        fr=(
            f"Ces jobs ont échoué dans le dernier pipeline : {echoues} (statut "
            f"du pipeline « {statut} »)."
        ),
    )
    assert statut in ("success", "manual"), message(
        en=(
            f"The latest pipeline on the default branch is '{statut}'. Expected "
            "'success', or 'manual' while a manual job is still waiting."
        ),
        fr=(
            f"Le dernier pipeline de la branche par défaut est « {statut} ». "
            "Attendu « success », ou « manual » tant qu'un job manuel attend."
        ),
    )
