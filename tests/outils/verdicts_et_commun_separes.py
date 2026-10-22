#!/usr/bin/env python3
"""Un verdict ne se commite pas avec ce qu'il mesure.

POURQUOI CE GARDE-FOU EXISTE

Le 2026-10-22, une correction de `labs/_commun/` et les verdicts qu'elle
rendait caducs sont partis dans le MEME commit. Le defaut est passe inapercu
plusieurs heures, et pas par inattention : le generateur du registre, cote
site, classe un lab « a reattester » quand un commit POSTERIEUR a son verdict
touche ses fichiers. Verdicts et modification du commun etant dans le meme
commit, aucun verdict n'etait posterieur a quoi que ce soit, et le controle
concluait que tout allait bien.

La correction elle-meme etait juste : elargir le patch du registre local a
tous les fichiers de pipeline. Mais elle employait `ansible.builtin.find`, qui
IGNORE LES FICHIERS CACHES par defaut, et `.gitlab-ci.yml` commence par un
point. Elle a donc repare les labs dont le service vit dans `ci/*.yml` et
casse en silence tous ceux dont le service vit a la racine. Vingt et un
verdicts VALIDE ne valaient plus rien, et rien ne le disait.

CE QUE CE CONTROLE IMPOSE

L'ordre, et qu'il soit VISIBLE dans l'historique :

    1. le correctif du commun, dans son commit ;
    2. la campagne de validation ;
    3. le releve, dans un commit qui ne change rien d'autre.

Un verdict n'est lisible que s'il est ecrit par un commit qui ne modifie pas ce
qu'il mesure. Autrement, « ce verdict est-il encore valable ? » n'a plus de
reponse mecanique, et il faut croire l'auteur sur parole.

CE QU'IL NE PEUT PAS FAIRE

Il ne verifie pas que la campagne a REELLEMENT tourne entre les deux commits :
rien dans un depot git ne le prouve. Il rend seulement la question posable.
"""

from __future__ import annotations

import subprocess
import sys

# Ce qu'un verdict mesure, et qui ne doit donc pas bouger dans le commit qui
# l'inscrit. `labs/` en entier serait trop large : un commit qui corrige UN
# lab et reinscrit SON verdict est legitime et frequent. Ce qui est interdit,
# c'est de toucher le COMMUN, qui porte tous les labs a la fois, ou l'outillage
# qui produit le verdict lui-meme.
PARTAGE = ("labs/_commun/", "scripts/")
RELEVE = "validation-labs.json"


def fichiers_indexes() -> list[str]:
    issue = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if issue.returncode != 0:
        print(f"git a repondu {issue.returncode} : {issue.stderr.strip()}", file=sys.stderr)
        # Ne rien pouvoir mesurer n'est pas « tout va bien » : on sort en 2.
        sys.exit(2)
    return [ligne for ligne in issue.stdout.splitlines() if ligne]


def main() -> int:
    indexes = fichiers_indexes()
    if RELEVE not in indexes:
        return 0

    fautifs = [f for f in indexes if f.startswith(PARTAGE)]
    if not fautifs:
        return 0

    print(
        f"REFUS : ce commit inscrit « {RELEVE} » ET modifie ce que les verdicts\n"
        "mesurent :\n",
        file=sys.stderr,
    )
    for f in sorted(fautifs):
        print(f"  {f}", file=sys.stderr)
    print(
        "\nUn verdict ecrit dans le meme commit que le code partage qu'il mesure\n"
        "n'est verifiable par personne : le controle de peremption compare les\n"
        "dates de commit, et il n'y a plus rien a comparer. C'est exactement\n"
        "ainsi que vingt et un verdicts sont restes VALIDE le 2026-10-22 alors\n"
        "qu'un defaut du commun les avait tous perimes.\n"
        "\n"
        "Faire deux commits, dans cet ordre :\n"
        "\n"
        "  git reset HEAD validation-labs.json   # sortir le releve de l'index\n"
        "  git commit                            # le correctif, seul\n"
        "  python3 scripts/valider-labs.py       # la campagne, apres lui\n"
        "  git add validation-labs.json && git commit\n",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
