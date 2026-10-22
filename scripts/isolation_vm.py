"""Isolation des labs : ici, c'est le setup qui la porte.

Le catalogue Linux, d'ou vient `valider-labs.py`, ramene ses VM a une base
figee entre deux labs (overlay qcow2 sous KVM). Ce catalogue n'en a pas
besoin, et c'est un choix mesure : remettre GitLab CE a une base figee
couterait un redemarrage complet de l'instance, soit plusieurs minutes a
chaque lab. A la place, chaque `setup.yaml` rejoue le socle commun (GitLab CE,
son runner, le jeton d'administration), puis SUPPRIME et RECREE le projet
`pipeline-craft` dans la forge, sa copie locale, et EFFACE les pipelines du
projet. L'etat note par les tests ne depend donc pas du lab joue juste avant.

Ce module garde l'interface attendue par `valider-labs.py` et ne fait rien.
"""

from __future__ import annotations

from pathlib import Path


class IsolationEteinte(RuntimeError):
    """Jamais levee ici : ce catalogue n'a pas d'isolation par snapshot."""


def hotes_du_lab(lab_root: Path) -> list[str]:
    del lab_root  # signature imposee par dsoxlab, sans objet ici
    return []


def snapshot_reset(hotes: list[str]) -> None:
    del hotes  # signature imposee par dsoxlab, sans objet ici
    return None
