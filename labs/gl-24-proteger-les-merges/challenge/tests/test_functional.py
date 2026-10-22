"""Tests du lab gl-24-proteger-les-merges.

CE LAB NOTE LES VERROUS QUE LA FORGE PORTE, JAMAIS CE QUI EST ECRIT. Une
branche protegee, un tag protege et deux reglages de
fusion sont des donnees du SERVEUR : un `.gitlab-ci.yml` ne les contient pas et
ne prouve rien d'eux. Les tests les lisent dans l'API de GitLab.

LA REGLE DU CATALOGUE : l'etat de depart est un projet SANS AUCUN verrou, et le
setup l'a mesure (diagnostic ecrit dans /var/tmp/gl-24-diagnostic-depart.txt).
Chacun des cinq tests porte donc sur une absence, aucun ne peut etre vert au
depart :
  1. `main` n'est pas protegee ;
  2. aucun tag de release n'est protege ;
  3. la fusion n'exige pas de pipeline vert ;
  4. la fusion n'exige pas de discussions resolues ;
  5. aucun pipeline n'a tourne depuis le depart : prouver que les verrous
     laissent passer un deploiement legitime.

CE QUE LES TESTS NE FONT PAS. Ils n'imposent ni la facon de poser les verrous
(interface ou API), ni le motif exact du tag (`v*`, `v1.*`, `*`: tout motif qui
couvre `v1.0.0` convient).

ECART ASSUME, A LIRE AVANT DE CROIRE A « PROTEGE ». GitLab 19.5.1 CE ne date
pas la pose d'un verrou. Le test 6 prouve qu'un pipeline a reussi APRES le
depart, pas qu'il a reussi APRES la pose des verrous : un apprenant qui lance
le pipeline d'abord et pose les verrous ensuite serait accepte. Il ne mesure
pas non plus le comportement (un push refuse, une fusion bloquee) : il mesure
le reglage qui le produit. La regle « approval rule » et l'environnement protege sont Premium (l'API
`protected_environments` repond 404 sur cette instance CE, mesure du
2026-10-22) : hors perimetre, ni demandes ni testes.
"""

from __future__ import annotations

import fnmatch
import sys
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

ETAT = "/var/lib/dsoxlab/gl-24"
JOB_TEST = "tester"
JOB_DEPLOI = "deployer-production"
ENCOURS = ("created", "pending", "running", "waiting_for_resource", "preparing")
# 0 personne, 30 Developer, 40 Maintainer, 60 administrateur.
NIVEAUX_RESERVES = (0, 40, 60)


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


def _niveaux(liste) -> list[int]:
    return [x.get("access_level") for x in (liste or []) if isinstance(x, dict)]


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


def test_main_protegee_en_ecriture_et_en_fusion(forge, projet_du_lab) -> None:
    """main est protegee : ni push direct pour un Developer, ni force push, fusion permise."""
    b = api(forge, f"/projects/{projet_du_lab['id']}/protected_branches/main")
    assert isinstance(b, dict) and b.get("name") == "main", message(
        en=(
            "The main branch is not protected. Anyone with the Developer role can "
            "push to it directly and rewrite its history: a merge request "
            "protects nothing if the branch accepts a direct push."
        ),
        fr=(
            "La branche main n'est pas protégée. Tout Developer peut y pousser "
            "directement et réécrire son historique : une merge request ne "
            "protège rien si la branche accepte un push direct."
        ),
    )
    push = _niveaux(b.get("push_access_levels"))
    assert push and all(n in NIVEAUX_RESERVES for n in push), message(
        en=(
            f"Who may push to main: access levels {push}. A Developer (30) can "
            "still push directly. Allow only Maintainers (40) or no one (0)."
        ),
        fr=(
            f"Qui peut pousser sur main : niveaux d'accès {push}. Un Developer "
            "(30) peut encore pousser directement. N'autorisez que les "
            "Maintainers (40) ou personne (0)."
        ),
    )
    assert b.get("allow_force_push") is False, message(
        en="Force push is allowed on main: the history can be rewritten.",
        fr="Le push forcé est autorisé sur main : l'historique peut être réécrit.",
    )
    fusion = _niveaux(b.get("merge_access_levels"))
    assert fusion and all(n in (30, 40, 60) for n in fusion), message(
        en=(
            f"Who may merge into main: access levels {fusion}. Someone must be "
            "able to merge (Developers or Maintainers), otherwise no change can "
            "ever reach main."
        ),
        fr=(
            f"Qui peut fusionner dans main : niveaux d'accès {fusion}. Quelqu'un "
            "doit pouvoir fusionner (Developers ou Maintainers), sinon aucun "
            "changement n'atteint jamais main."
        ),
    )


def test_tags_de_release_proteges(forge, projet_du_lab) -> None:
    """Un motif de tag protege couvre v1.0.0 et reserve sa creation."""
    tags = api(forge, f"/projects/{projet_du_lab['id']}/protected_tags")
    tags = tags if isinstance(tags, list) else []
    couvrants = [t for t in tags if fnmatch.fnmatch("v1.0.0", t.get("name", ""))]
    assert couvrants, message(
        en=(
            f"No protected tag covers a release tag such as v1.0.0 (protected "
            f"patterns: {[t.get('name') for t in tags]}). Anyone with the "
            "Developer role can create a release tag, and a tag is what a "
            "release pipeline deploys. Protect a pattern such as v*."
        ),
        fr=(
            f"Aucun tag protégé ne couvre un tag de release comme v1.0.0 (motifs "
            f"protégés : {[t.get('name') for t in tags]}). Tout Developer peut "
            "créer un tag de release, et c'est un tag que déploie un pipeline "
            "de release. Protégez un motif comme v*."
        ),
    )
    for t in couvrants:
        niveaux = _niveaux(t.get("create_access_levels"))
        assert niveaux and all(n in NIVEAUX_RESERVES for n in niveaux), message(
            en=(
                f"The protected tag {t.get('name')!r} can be created by access "
                f"levels {niveaux}: a Developer (30) can still create it. Allow "
                "only Maintainers (40)."
            ),
            fr=(
                f"Le tag protégé {t.get('name')!r} peut être créé par les niveaux "
                f"d'accès {niveaux} : un Developer (30) peut encore le créer. "
                "N'autorisez que les Maintainers (40)."
            ),
        )


def test_pipeline_vert_exige_avant_fusion(forge, projet_du_lab) -> None:
    """Le projet refuse de fusionner une merge request sans pipeline vert."""
    p = api(forge, f"/projects/{projet_du_lab['id']}")
    assert isinstance(p, dict) and p.get("only_allow_merge_if_pipeline_succeeds") is True, message(
        en=(
            "Merging does not require a successful pipeline "
            "(only_allow_merge_if_pipeline_succeeds is off). A merge request "
            "with a red pipeline can be merged."
        ),
        fr=(
            "La fusion n'exige pas de pipeline vert "
            "(only_allow_merge_if_pipeline_succeeds est désactivé). Une merge "
            "request au pipeline rouge peut être fusionnée."
        ),
    )


def test_discussions_resolues_exigees_avant_fusion(forge, projet_du_lab) -> None:
    """Le projet refuse de fusionner tant qu'une discussion de revue reste ouverte."""
    p = api(forge, f"/projects/{projet_du_lab['id']}")
    assert isinstance(p, dict) and p.get("only_allow_merge_if_all_discussions_are_resolved") is True, message(
        en=(
            "Merging does not require resolved discussions "
            "(only_allow_merge_if_all_discussions_are_resolved is off). A remark "
            "left open by a reviewer does not stop the merge."
        ),
        fr=(
            "La fusion n'exige pas de discussions résolues "
            "(only_allow_merge_if_all_discussions_are_resolved est désactivé). "
            "Une remarque laissée ouverte par un relecteur n'empêche pas la fusion."
        ),
    )


def test_les_verrous_laissent_passer_un_deploiement_legitime(forge, projet_du_lab) -> None:
    """Un pipeline lance depuis le depart reussit : les verrous ne ferment pas la porte a tous."""
    pid = projet_du_lab["id"]
    depart = _depart(forge)
    apres = sorted(
        (p for p in pipelines(forge, ref="main", projet_id=pid) if p["id"] > depart),
        key=lambda p: p["id"],
        reverse=True,
    )
    assert apres, message(
        en=(
            "No pipeline has run on main since the lab started. Locks that "
            "forbid everything are not protection: run a pipeline on main and "
            "check that the production deployment still goes through."
        ),
        fr=(
            "Aucun pipeline n'a tourné sur main depuis le début du lab. Des "
            "verrous qui interdisent tout ne protègent rien : lancez un "
            "pipeline sur main et vérifiez que le déploiement en production "
            "passe toujours."
        ),
    )
    dernier = apres[0]
    assert dernier.get("status") not in ENCOURS, message(
        en=f"The latest pipeline is still {dernier.get('status')}. Wait for it, then run the check again.",
        fr=f"Le dernier pipeline est encore {dernier.get('status')}. Attendez-le, puis relancez la vérification.",
    )
    liste = jobs(forge, dernier["id"], pid)
    par_nom = {j["name"]: j for j in liste}
    mauvais = [f"{j['name']} ({j['status']})" for j in liste if j["status"] in ("failed", "canceled")]
    assert not mauvais, message(
        en=(
            f"The latest pipeline has failed jobs: {', '.join(mauvais)}. Read the "
            "log of the failed job."
        ),
        fr=(
            f"Le dernier pipeline a des jobs en échec : {', '.join(mauvais)}. "
            "Lisez le journal du job en échec."
        ),
    )
    for nom in (JOB_TEST, JOB_DEPLOI):
        assert nom in par_nom and par_nom[nom]["status"] == "success", message(
            en=f"The job {nom} must exist and pass in the latest pipeline of main.",
            fr=f"Le job {nom} doit exister et réussir dans le dernier pipeline de main.",
        )
