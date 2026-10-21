#!/usr/bin/env bash
# Fabrique le depot fil rouge que les labs poussent dans la forge.
#
# POURQUOI UN BUNDLE, ET POURQUOI PAS UNE COPIE DES FICHIERS
#
# Les 19 pages de lab du site decrivent le depot REEL `pipeline-craft`
# (gitlab.com `Bob74/pipeline-craft`, clone dans ~/Projets/lab-gitlab-cicd),
# avec ses chemins (`app/main.py`, `requirements-dev.txt`), ses messages
# d'erreur releves a l'execution, et surtout sa convention de branches :
# `starter/lab-NN` est l'etat de depart du lab N, `solution/lab-NN` son
# corrige. Arbitrage de Stephane du 2026-10-21 : « les labs sur gitlab.com
# sont les bons ».
#
# Reconstruire une arborescence differente dans le catalogue ferait DIVERGER
# la consigne de son corrige : l'apprenant lirait `app/main.py` sur le site et
# trouverait autre chose dans la forge. Le depot arrive donc tel quel, avec son
# historique, par un bundle git.
#
# CE QUI N'ENTRE PAS DANS LE BUNDLE : les branches `solution/*`. Elles sont la
# reponse. Elles restent cote formateur, ou les playbooks de `solution/` vont
# les chercher pour prouver que le lab se reussit. Pousser la solution dans la
# forge que l'on note rendrait la note sans valeur.
#
# Taille mesuree le 2026-10-21 : 67 Ko pour `main` et les 19 branches
# `starter/`, soit un fichier versionnable sans remords.
set -euo pipefail

SOURCE=${SOURCE:-$HOME/Projets/lab-gitlab-cicd}
CIBLE="$(cd "$(dirname "$0")/.." && pwd)/labs/_commun/depot/pipeline-craft.bundle"

if [ ! -d "$SOURCE/.git" ]; then
  echo "depot source introuvable : $SOURCE" >&2
  echo "clonez d'abord gitlab.com/Bob74/pipeline-craft a cet emplacement." >&2
  exit 1
fi

cd "$SOURCE"

# `git bundle` refuse une reference absente : on liste ce qui existe vraiment
# plutot que d'ecrire les 19 noms a la main.
mapfile -t STARTERS < <(git branch --format='%(refname:short)' | grep '^starter/' | sort -V)
if [ "${#STARTERS[@]}" -eq 0 ]; then
  echo "aucune branche starter/ dans $SOURCE : rien a mettre dans le bundle" >&2
  exit 1
fi

mkdir -p "$(dirname "$CIBLE")"
git bundle create "$CIBLE" main "${STARTERS[@]}" >/dev/null

# Un bundle se verifie, et c'est la moitie du travail : un bundle tronque se
# pousse sans broncher et casse le lab plus tard, loin de sa cause.
git bundle verify "$CIBLE" >/dev/null

echo "bundle ecrit : $CIBLE"
echo "  references : main + ${#STARTERS[@]} branche(s) starter/"
echo "  taille     : $(du -h "$CIBLE" | cut -f1)"
echo "  empreinte  : $(sha256sum "$CIBLE" | cut -c1-16)…"
