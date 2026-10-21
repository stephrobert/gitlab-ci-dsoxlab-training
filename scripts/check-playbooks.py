#!/usr/bin/env python3
"""Chaque playbook du catalogue se CHARGE-t-il ?

POURQUOI CE CONTROLE EXISTE, ET POURQUOI IL N'EST PAS UN LINTER DE PLUS

Deux fois le 2026-10-21, un playbook a ete refuse par Ansible AU CHARGEMENT,
avant d'executer la moindre tache, avec le meme message :

    failed at splitting arguments, either an unbalanced jinja2 block or quotes

Les deux causes etaient invisibles a la lecture, et toutes deux dans un script
shell embarque par un bloc litteral :

  - `${#JETON}` pour mesurer la longueur d'une variable. Jinja lit `{#` comme
    le debut d'un commentaire et cherche le `#}` correspondant.
  - une APOSTROPHE dans un commentaire francais (« la solution n'est plus
    idempotente »). Ansible decoupe la chaine a la facon d'un shell, et une
    apostrophe peut y ouvrir une citation qui ne se ferme jamais.

    CE QU'ON NE SAIT PAS, ET IL FAUT LE DIRE : la regle exacte. Mesure par
    isolement le 2026-10-21, un bloc avec UNE apostrophe de commentaire est
    refuse ; un autre avec QUATRE passe ; un troisieme avec TROIS passe aussi.
    La parite ne suffit donc pas a predire le refus, et aucune regle simple
    n'a resiste a la mesure. C'est precisement pourquoi ce controle existe
    sous cette forme : le seul juge fiable est Ansible lui-meme.

    Consequence pratique a l'ecriture : les explications d'un script embarque
    montent en commentaire YAML, AU-DESSUS de la tache, ou l'apostrophe ne
    risque rien.

La consequence est la pire possible : rien ne tourne, le message ne nomme pas
la ligne fautive, et le lab semble casse pour une autre raison. Un controle de
forme ne suffirait pas : seul le chargement reel par Ansible prouve qu'un
playbook se charge, et c'est la regle du depot (« le controle doit porter sur
le comportement, pas sur la forme »).

Usage :

    python3 scripts/check-playbooks.py          # tous les playbooks
    python3 scripts/check-playbooks.py <f> ...  # ceux qu'on nomme
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
VAULT = RACINE / ".vault-pass"


def playbooks() -> list[Path]:
    """Les playbooks du catalogue, solutions chiffrees comprises.

    `labs/_commun/socle.yaml` est importe par les setups, donc deja couvert,
    mais on le verifie aussi seul : une erreur de chargement y casserait tous
    les labs d'un coup, et le message ne dirait pas lequel.
    """
    trouves: list[Path] = []
    for motif in ("labs/**/setup.yaml", "labs/**/cleanup.yaml",
                  "labs/_commun/*.yaml", "solution/**/solution.yaml",
                  "solution-en-clair/**/solution.yaml"):
        trouves.extend(sorted(RACINE.glob(motif)))
    return [f for f in dict.fromkeys(trouves) if f.is_file()]


def est_un_playbook(fichier: Path) -> bool:
    """Un playbook declare des plays (`hosts:`) ; un fichier de taches, non.

    `labs/_commun/depot.yaml` est une LISTE DE TACHES, incluse par chaque
    setup. Passe tel quel a `--syntax-check`, il rend
    « 'ansible.builtin.file' is not a valid attribute for a Play » : le
    controle mesurerait alors sa propre meprise, pas le fichier. On ne
    l'ecarte pas pour autant, on l'enveloppe (voir `charge`), parce que c'est
    justement le fichier le plus partage du catalogue.
    """
    try:
        import yaml  # dependance deja presente dans le catalogue

        doc = yaml.safe_load(fichier.read_text())
    except Exception:
        # Illisible ou chiffre (ansible-vault) : on laisse Ansible trancher.
        return True
    if not isinstance(doc, list) or not doc:
        return True
    return any(isinstance(e, dict) and "hosts" in e for e in doc)


def charge(fichier: Path) -> tuple[bool, str]:
    enveloppe: Path | None = None
    if not est_un_playbook(fichier):
        enveloppe = RACINE / f".check-taches-{fichier.stem}.yml"
        enveloppe.write_text(
            "---\n"
            "# Enveloppe temporaire, ecrite par scripts/check-playbooks.py pour\n"
            "# charger un FICHIER DE TACHES comme Ansible le fera a l'execution.\n"
            "- name: Enveloppe de controle\n"
            "  hosts: localhost\n"
            "  gather_facts: false\n"
            "  tasks:\n"
            # Chemin ABSOLU : un `relative_to` levait ValueError des qu'on
            # nommait un fichier hors du catalogue, ce qui est exactement ce
            # qu'on fait pour eprouver ce controle.
            f"    - ansible.builtin.import_tasks: {fichier.resolve()}\n"
        )
        cible = enveloppe
    else:
        cible = fichier

    cmd = ["ansible-playbook", "--syntax-check", str(cible)]
    if VAULT.is_file():
        cmd += ["--vault-password-file", str(VAULT)]
    try:
        r = subprocess.run(cmd, cwd=RACINE, capture_output=True, text=True)
    finally:
        if enveloppe is not None:
            enveloppe.unlink(missing_ok=True)
    if r.returncode == 0:
        return True, ""
    # Le message utile est sur stderr, et la ligne qui nomme la cause est
    # noyee dans la banniere de version d'ansible-playbook.
    lignes = [
        l for l in (r.stdout + r.stderr).splitlines()
        if "ERROR" in l or "failed at splitting" in l or "Origin:" in l
    ]
    return False, "\n      ".join(lignes[:4]) or "(aucun message lisible)"


def main() -> int:
    cibles = [Path(a).resolve() for a in sys.argv[1:]] or playbooks()
    if not cibles:
        print("aucun playbook trouve")
        return 0

    echecs = 0
    for f in cibles:
        ok, message = charge(f)
        rel = f.relative_to(RACINE) if RACINE in f.parents else f
        if ok:
            print(f"  ok     {rel}")
        else:
            echecs += 1
            print(f"  REFUSE {rel}\n      {message}")

    print()
    if echecs:
        print(f"{echecs} playbook(s) ne se chargent pas. Cherchez, dans les scripts")
        print("embarques : une apostrophe isolee dans un commentaire, ou un")
        print("`${#...}` que Jinja lit comme un commentaire ouvert.")
        return 1
    print(f"{len(cibles)} playbook(s) se chargent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
