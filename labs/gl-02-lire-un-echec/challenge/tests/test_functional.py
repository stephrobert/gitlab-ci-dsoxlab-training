"""Tests du lab gl-02-lire-un-echec.

ON NOTE LES TROIS BUGS, UN PAR UN, ET PAS SEULEMENT LE VERT FINAL. C'est le
choix qui distingue ce lab du precedent, et il vient d'un raisonnement simple :
un pipeline vert ne prouve pas ici que le travail est fait. Un apprenant qui
retire le job de lint obtient du vert sans avoir corrige une seule ligne, et un
apprenant qui commente l'import au lieu de le supprimer passe le lint sans
avoir compris le message de ruff.

Les quatre tests mesurent donc, dans l'ordre des trois bugs :

- la configuration est ACCEPTEE par GitLab (bug 1, le stage qui n'existe pas) ;
- les deux imports inutiles ont disparu DU CODE dans la forge (bugs 2 et 3) ;
- le dernier pipeline de la branche par defaut est vert ;
- le lint ET les tests ont tourne et reussi, reconnus par leurs JOURNAUX, pas
  par le nom des jobs : un apprenant est libre de les renommer.

CE QU'ON NE VERIFIE PAS, ET C'EST VOULU. Ni le nom des jobs, ni la facon de
corriger la configuration, ni l'ordre des imports restants. Ruff compte quatre
erreurs pour deux bugs, les imports inutiles cassant aussi l'ordre du bloc
(regle I001) ; corriger la cause fait disparaitre les deux, et c'est le lint du
serveur qui en juge, pas ce fichier.
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
    fichier,
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
    """Garde-fou : sans forge joignable, aucun test ne mesure l'apprenant.

    GitLab met plusieurs minutes a repondre au premier demarrage. Sans ce
    garde-fou, tous les tests echoueraient et l'apprenant chercherait une faute
    qu'il n'a pas commise.
    """
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


def test_la_configuration_est_acceptee(forge, projet_du_lab):
    """Bug 1 : un job visait un stage absent de la liste `stages:`.

    GitLab valide le fichier AVANT de creer les jobs : un stage inconnu fait
    refuser le pipeline entier, qui apparait rouge sans un seul job. Le linter
    du projet est l'endroit ou GitLab explique ce refus, et c'est pour cela
    qu'on l'interroge au lieu de relire le YAML nous-memes.
    """
    rapport = lint_configuration(forge, projet_du_lab["id"])
    assert rapport is not None, message(
        en="GitLab's CI linter did not answer; the configuration could not be checked.",
        fr="Le linter CI de GitLab n'a pas répondu : la configuration n'a pas pu être vérifiée.",
    )
    erreurs = rapport.get("errors") or []
    assert rapport.get("valid") is True, message(
        en=f"GitLab still refuses the configuration: {erreurs}",
        fr=f"GitLab refuse encore la configuration : {erreurs}",
    )


def test_les_imports_inutiles_ont_disparu(forge, projet_du_lab):
    """Bugs 2 et 3 : deux imports inutilises que seul le lint signalait.

    On lit les fichiers DANS LA FORGE, pas sur la machine : ce qui compte est
    ce que le serveur a recu. Un fichier corrige localement mais jamais pousse
    laisse le pipeline rouge.
    """
    attendus = [
        ("app/main.py", "import os"),
        ("app/routes/health.py", "import httpx"),
    ]
    restants = []
    for chemin, ligne in attendus:
        contenu = fichier(forge, chemin, projet_id=projet_du_lab["id"])
        assert contenu is not None, message(
            en=f"{chemin} was not found in the repository on the default branch.",
            fr=f"{chemin} est introuvable dans le dépôt, sur la branche par défaut.",
        )
        # Une ligne commentee reste un defaut : ruff ne la signale plus, mais le
        # code garde une trace morte, et le lab demande de SUPPRIMER l'import.
        for brute in contenu.splitlines():
            if brute.strip() == ligne:
                restants.append(f"{chemin} : {ligne}")
    assert not restants, message(
        en=(
            f"These unused imports are still in the repository: {restants}. "
            "Ruff said 'imported but unused': such an import is removed."
        ),
        fr=(
            f"Ces imports inutiles sont encore dans le dépôt : {restants}. "
            "Ruff dit « imported but unused » : un import inutilisé se supprime."
        ),
    )


def test_le_pipeline_est_vert(forge, projet_du_lab):
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch since your corrections.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut depuis vos corrections.",
    )
    statut = dernier.get("status")
    assert statut == "success", message(
        en=f"The latest pipeline on the default branch is '{statut}', not 'success'.",
        fr=f"Le dernier pipeline de la branche par défaut est « {statut} », pas « success ».",
    )


def test_le_lint_et_les_tests_ont_reussi(forge, projet_du_lab):
    """Le vert ne suffit pas : il faut que les deux gestes aient tourne.

    LE PIEGE QUE CE TEST FERME : retirer le job de lint rend le pipeline vert
    sans avoir corrige le code. Les deux gestes se reconnaissent dans les
    JOURNAUX des jobs reussis, jamais a leur nom.
    """
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch since your corrections.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut depuis vos corrections.",
    )
    tous = jobs(forge, dernier["id"], projet_du_lab["id"])
    reussis = [j for j in tous if j.get("status") == "success"]

    traces = ""
    for j in reussis:
        brut = api(
            forge,
            f"/projects/{projet_du_lab['id']}/jobs/{j['id']}/trace",
            brut=True,
        )
        if brut:
            traces += brut.lower()

    gestes = {
        "lint": ("ruff", "flake8", "pylint"),
        "tests": ("pytest", "test session", "passed"),
    }
    manquants = [
        nom for nom, motifs in gestes.items()
        if not any(m in traces for m in motifs)
    ]
    assert not manquants, message(
        en=(
            f"No trace of these steps in the successful jobs' logs: {manquants}. "
            "A pipeline that is green because a job was removed proves nothing."
        ),
        fr=(
            f"Aucune trace de ces étapes dans les journaux des jobs réussis : "
            f"{manquants}. Un pipeline vert parce qu'un job a été retiré ne "
            "prouve rien."
        ),
    )
