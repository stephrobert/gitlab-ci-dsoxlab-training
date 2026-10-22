"""Une forge absente ne doit pas se lire comme un lab faux.

POURQUOI CE TEST EXISTE

Le 2026-10-22, la VM du catalogue etait eteinte et trois cycles ont ete lances
dessus. Les setups ont echoue en onze secondes sur « Failed to connect to the
host via ssh: No route to host », et `valider-labs.py` a inscrit trois ROUGE
avec des scores `None` dans `validation-labs.json`.

Les trois labs etaient justes. Le releve, lui, accusait le catalogue de ce qui
manquait au POSTE, et il se lit comme une mesure : c'est exactement ce que ce
depot pretend interdire. `verdict_check` portait deja la distinction (SKIP, et
le code de sortie 10, « a remesurer »), mais elle n'etait pas cablee sur
l'echec de `run`, qui est le chemin emprunte quand la machine est eteinte.

CE QUE CE TEST CONTROLE, ET DANS LES DEUX SENS

Un controle qui ne verifierait que le cas injoignable serait satisfait par une
fonction qui rend toujours vrai, et tout echec de setup deviendrait alors un
SKIP silencieux : le defaut inverse, et le pire des deux. Les deux sens sont
donc eprouves.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]

# `valider-labs.py` porte un tiret : il ne s'importe pas par son nom. On le
# charge par son chemin, et `scripts/` entre dans le sys.path parce que le
# script importe lui-meme ses voisins (verdict_check, isolation_vm).
sys.path.insert(0, str(RACINE / "scripts"))
_spec = importlib.util.spec_from_file_location(
    "valider_labs", RACINE / "scripts" / "valider-labs.py"
)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
# Inscrit AVANT l'execution : `@dataclass` resout les annotations par
# `sys.modules[cls.__module__].__dict__`, et leve un AttributeError sur None
# si le module n'y est pas encore.
sys.modules["valider_labs"] = _module
_spec.loader.exec_module(_module)
machine_injoignable = _module.machine_injoignable


# Sorties reelles, recopiees telles qu'Ansible et ssh les ecrivent.
INJOIGNABLES = [
    "fatal: [gitlab-1.lab]: UNREACHABLE! => {\"changed\": false, \"msg\": "
    "\"Failed to connect to the host via ssh: ssh: connect to host "
    "10.10.95.11 port 22: No route to host\", \"unreachable\": true}",
    "gitlab-1.lab : ok=0 changed=0 unreachable=1 failed=0",
    "ssh: connect to host 10.10.95.11 port 22: Connection timed out",
    "ssh: Could not resolve hostname gitlab-1.lab: Name or service not known",
    "Host key verification failed.",
]

# Des echecs qui sont bien des defauts du lab ou de son setup, et qui doivent
# rester ROUGE.
DEFAUTS_REELS = [
    "fatal: [gitlab-1.lab]: FAILED! => {\"msg\": \"The task includes an option "
    "with an undefined variable\"}",
    "ERROR! 'ansible.builtin.file' is not a valid attribute for a Play",
    "fatal: [gitlab-1.lab]: FAILED! => {\"changed\": true, \"cmd\": "
    "\"gitlab-rails runner ...\", \"rc\": 1, \"stderr\": \"undefined method\"}",
    "TASK [Creer le projet] *** fatal: [gitlab-1.lab]: FAILED! => "
    "{\"status\": 403, \"msg\": \"403 Forbidden\"}",
    "",
]


@pytest.mark.parametrize("sortie", INJOIGNABLES)
def test_une_machine_absente_est_reconnue(sortie: str) -> None:
    assert machine_injoignable(sortie), (
        "Cette sortie dit que l'HOTE n'a pas repondu. La prendre pour un defaut "
        "du lab inscrirait un ROUGE sur une forge absente, ce qui se lit comme "
        f"une mesure alors que rien n'a ete mesure.\nSortie : {sortie[:160]}"
    )


@pytest.mark.parametrize("sortie", DEFAUTS_REELS)
def test_un_vrai_defaut_reste_un_defaut(sortie: str) -> None:
    assert not machine_injoignable(sortie), (
        "Cette sortie est un echec du setup ou du lab, pas une machine "
        "absente. La classer en « injoignable » la ferait passer en SKIP, "
        "c'est-a-dire en « a remesurer », et un defaut reel disparaitrait du "
        f"releve sans un mot.\nSortie : {sortie[:160]}"
    )


def test_la_casse_ne_change_rien() -> None:
    """Ansible ecrit UNREACHABLE en capitales, ssh ecrit « No route » autrement."""
    assert machine_injoignable("NO ROUTE TO HOST")
    assert machine_injoignable("no route to host")
