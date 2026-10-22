"""L'empreinte doit bouger quand la mesure change, et SEULEMENT alors.

Les deux sens comptent autant l'un que l'autre, et le second davantage :

- une empreinte qui ne bougerait pas sur un changement de test laisserait
  passer un verdict perime, ce qui est le sens dangereux ;
- une empreinte qui bougerait sur une coquille d'enonce ferait basculer tout
  le catalogue en « a reattester » pour rien, et on apprendrait a ignorer le
  statut, ce qui revient au meme a deux semaines.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "empreinte_lab", RACINE / "scripts" / "empreinte_lab.py"
)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
sys.modules["empreinte_lab"] = _module
_spec.loader.exec_module(_module)
empreinte = _module.empreinte

PARTAGES = ("conftest.py", "labs/_commun")


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    """Un catalogue minimal, avec un lab complet et ce qui l'entoure."""
    lab = tmp_path / "labs" / "demo"
    (lab / "challenge" / "tests").mkdir(parents=True)
    (lab / "challenge" / "work").mkdir(parents=True)
    (lab / "lab.yaml").write_text("id: demo\n", encoding="utf-8")
    (lab / "setup.yaml").write_text("- hosts: lab_target\n", encoding="utf-8")
    (lab / "cleanup.yaml").write_text("- hosts: lab_target\n", encoding="utf-8")
    (lab / "challenge" / "tests" / "test_functional.py").write_text(
        "def test_un():\n    assert True\n", encoding="utf-8"
    )
    # Ce qui ne doit PAS compter.
    (lab / "README.md").write_text("enonce\n", encoding="utf-8")
    (lab / "scenario.md").write_text("scenario\n", encoding="utf-8")
    (lab / "challenge" / "hints.yaml").write_text("hints: []\n", encoding="utf-8")
    (lab / "challenge" / "work" / "brouillon.txt").write_text("travail\n", encoding="utf-8")
    (tmp_path / "conftest.py").write_text("# commun\n", encoding="utf-8")
    commun = tmp_path / "labs" / "_commun"
    commun.mkdir(parents=True)
    (commun / "gitlab.py").write_text("def api():\n    pass\n", encoding="utf-8")
    (commun / "socle.yaml").write_text("- hosts: lab_target\n", encoding="utf-8")
    return tmp_path


def _empreinte(depot: Path) -> str:
    return empreinte(depot, "demo", PARTAGES)


def test_elle_est_stable_quand_rien_ne_bouge(depot: Path) -> None:
    assert _empreinte(depot) == _empreinte(depot)


# --- Ce qui DOIT faire bouger l'empreinte -----------------------------------

CE_QUI_COMPTE = [
    ("le test", "labs/demo/challenge/tests/test_functional.py", "def test_un():\n    assert False\n"),
    ("le setup", "labs/demo/setup.yaml", "- hosts: lab_target\n  tasks: []\n"),
    ("le cleanup", "labs/demo/cleanup.yaml", "- hosts: lab_target\n  tasks: []\n"),
    ("le lab.yaml", "labs/demo/lab.yaml", "id: demo\nruntime:\n  type: vm\n"),
    ("le conftest partage", "conftest.py", "# commun modifie\n"),
    ("le client d API commun", "labs/_commun/gitlab.py", "def api():\n    return 1\n"),
    ("le socle commun", "labs/_commun/socle.yaml", "- hosts: lab_target\n  tasks: []\n"),
]


@pytest.mark.parametrize(("titre", "relatif", "contenu"), CE_QUI_COMPTE, ids=[t for t, _, _ in CE_QUI_COMPTE])
def test_un_changement_de_la_mesure_perime_le_verdict(
    depot: Path, titre: str, relatif: str, contenu: str
) -> None:
    avant = _empreinte(depot)
    (depot / relatif).write_text(contenu, encoding="utf-8")
    assert _empreinte(depot) != avant, (
        f"Changer {titre} change ce que le cycle joue : le verdict precedent ne "
        "vaut plus, et l'empreinte doit le dire. Une empreinte sourde ici "
        "laisserait passer un verdict perime, qui est le sens dangereux de "
        "l'erreur."
    )


def test_un_test_ajoute_perime_le_verdict(depot: Path) -> None:
    avant = _empreinte(depot)
    (depot / "labs/demo/challenge/tests/test_autre.py").write_text(
        "def test_deux():\n    assert True\n", encoding="utf-8"
    )
    assert _empreinte(depot) != avant, "un test de plus change le bareme"


def test_un_test_renomme_perime_le_verdict(depot: Path) -> None:
    """Le NOM compte autant que le contenu : le lab ne joue plus le meme fichier."""
    avant = _empreinte(depot)
    base = depot / "labs/demo/challenge/tests"
    (base / "test_functional.py").rename(base / "test_renomme.py")
    assert _empreinte(depot) != avant


# --- Ce qui ne DOIT PAS la faire bouger -------------------------------------

CE_QUI_NE_COMPTE_PAS = [
    ("l'enonce", "labs/demo/README.md", "enonce corrige, une coquille en moins\n"),
    ("le scenario", "labs/demo/scenario.md", "scenario reecrit\n"),
    ("les indices", "labs/demo/challenge/hints.yaml", "hints:\n  - un indice\n"),
    ("le travail de l'apprenant", "labs/demo/challenge/work/brouillon.txt", "autre chose\n"),
]


@pytest.mark.parametrize(
    ("titre", "relatif", "contenu"), CE_QUI_NE_COMPTE_PAS, ids=[t for t, _, _ in CE_QUI_NE_COMPTE_PAS]
)
def test_ce_que_le_cycle_ne_joue_pas_ne_perime_rien(
    depot: Path, titre: str, relatif: str, contenu: str
) -> None:
    avant = _empreinte(depot)
    (depot / relatif).write_text(contenu, encoding="utf-8")
    assert _empreinte(depot) == avant, (
        f"Changer {titre} ne change pas ce que les tests mesurent. Faire "
        "basculer le lab en « a reattester » pour cela apprendrait a ignorer "
        "le statut, et un statut qu'on ignore ne protege plus de rien."
    )


def test_le_cache_python_ne_compte_pas(depot: Path) -> None:
    """`__pycache__` change a chaque version de Python : il rendrait tout instable."""
    avant = _empreinte(depot)
    cache = depot / "labs/demo/challenge/tests/__pycache__"
    cache.mkdir()
    (cache / "test_functional.cpython-314.pyc").write_bytes(b"\x00\x01binaire")
    assert _empreinte(depot) == avant


def test_deux_labs_distincts_ont_des_empreintes_distinctes(depot: Path) -> None:
    """Le chemin entre dans le calcul : deux labs au contenu identique diffèrent."""
    import shutil

    shutil.copytree(depot / "labs/demo", depot / "labs/demo2")
    assert empreinte(depot, "demo", PARTAGES) != empreinte(depot, "demo2", PARTAGES)


def test_une_correction_du_commun_perime_TOUS_les_labs(depot: Path) -> None:
    """Le defaut du 2026-10-22, retourne en controle.

    Une correction de `labs/_commun/` a peri me les vingt et un verdicts sans
    qu'aucun controle le dise, parce qu'elle avait ete commitee avec eux. Ce
    test dit que l'empreinte, elle, le voit : le commun entre dans l'empreinte
    de CHAQUE lab, donc le toucher les fait tous bouger a la fois.
    """
    import shutil

    shutil.copytree(depot / "labs/demo", depot / "labs/demo2")
    avant = {nom: empreinte(depot, nom, PARTAGES) for nom in ("demo", "demo2")}

    (depot / "labs/_commun/gitlab.py").write_text("def api():\n    return 2\n", encoding="utf-8")

    apres = {nom: empreinte(depot, nom, PARTAGES) for nom in ("demo", "demo2")}
    assert all(apres[n] != avant[n] for n in avant), (
        "Une correction du commun change ce que TOUS les labs jouent. Si "
        "l'empreinte n'en tenait pas compte, une campagne entiere resterait "
        "marquee attestee sur un commun qui n'existe plus, ce qui est "
        "exactement ce qui est arrive le 2026-10-22."
    )
