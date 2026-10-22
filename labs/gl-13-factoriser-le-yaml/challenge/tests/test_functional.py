"""Tests du lab gl-13-factoriser-le-yaml.

CE LAB EST LE SEUL DU CATALOGUE A LIRE LE FICHIER DE L'APPRENANT, et il faut
le dire franchement plutot que de le masquer.

Partout ailleurs, la note porte sur l'etat laisse sur la forge : un apprenant
qui atteint le bon etat par un autre chemin a reussi. Ici, l'etat ne peut PAS
servir de mesure, et c'est le sujet meme du lab : `extends` et les ancres YAML
sont RESOLUS avant l'execution. La configuration fusionnee que GitLab produit
est identique avant et apres la factorisation, et c'est precisement ce qu'on
demande de verifier. Un lab qui exigerait un changement d'etat demanderait donc
le contraire de son enonce.

UN SEUL TEST, QUI FAIT LES DEUX. Il lit le fichier DANS LA FORGE et y cherche
les deux mecaniques, un job cache reutilise par `extends:` et une ancre
fusionnee par `<<:`, sans dicter leurs noms ni leur nombre. Puis il verifie que
le comportement n'a PAS change : les jobs tournent toujours, aucun n'echoue, et
la couverture remonte encore.

CETTE SECONDE MOITIE EST CELLE QUI COMPTE LE PLUS, et elle n'est pas un test a
part pour une raison de principe : ses exigences sont vraies DES L'ETAT DE
DEPART, ou le pipeline est deja sain. Un test autonome passerait donc avant
tout travail, ce que `valider-labs.py` refuse. Un garde-fou s'ajoute au test
qui mesure le travail ; il ne tient pas debout seul.
"""

from __future__ import annotations

import re
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


def test_les_deux_mecaniques_de_factorisation_sont_la(forge, projet_du_lab):
    """Un job cache reutilise, et une ancre fusionnee.

    Les deux font le meme travail et ne se valent pas :

    - `extends:` est un mecanisme de GitLab. Il fusionne des JOBS, comprend les
      cles qu'il fusionne, et se lit dans l'interface ;
    - une ancre YAML est un mecanisme du FORMAT. Elle recopie n'importe quel
      fragment, y compris un bloc de variables, et GitLab n'en sait rien : elle
      est resolue avant qu'il ne lise le fichier.

    Le lab demande les deux pour que la difference se sente. Ni les noms ni le
    nombre ne sont imposes.
    """
    contenu = fichier(forge, ".gitlab-ci.yml", projet_id=projet_du_lab["id"])
    assert contenu, message(
        en="The .gitlab-ci.yml could not be read from the default branch.",
        fr="Le .gitlab-ci.yml n'a pas pu être lu sur la branche par défaut.",
    )

    # Un job cache se declare par un nom prefixe d'un point, au premier niveau.
    caches = set(re.findall(r"(?m)^\.([\w.-]+):", contenu))
    etendus = set(re.findall(r"(?m)^\s+extends:\s*\.?([\w.-]+)\s*$", contenu))
    etendus |= set(re.findall(r"(?m)^\s+-\s*\.([\w.-]+)\s*$", contenu))

    assert caches, message(
        en=(
            "No hidden job in the file. A hidden job starts with a dot "
            "(`.python-base:`) and never runs on its own: it exists to be "
            "reused."
        ),
        fr=(
            "Aucun job caché dans le fichier. Un job caché commence par un "
            "point (`.python-base:`) et ne tourne jamais seul : il existe pour "
            "être réutilisé."
        ),
    )
    assert "extends:" in contenu, message(
        en=(
            f"The file declares hidden job(s) ({sorted(caches)}) but no job "
            "extends them. A hidden job nobody extends is dead weight."
        ),
        fr=(
            f"Le fichier déclare un ou des jobs cachés ({sorted(caches)}) mais "
            "aucun job ne les étend. Un job caché que personne n'étend est du "
            "poids mort."
        ),
    )

    # Une ancre se declare par `&nom` et se fusionne par `<<: *nom`.
    ancres = set(re.findall(r"&([\w.-]+)", contenu))
    fusions = set(re.findall(r"<<:\s*\*([\w.-]+)", contenu))
    assert ancres and fusions, message(
        en=(
            f"No YAML anchor is merged in the file (anchors found: "
            f"{sorted(ancres)}, merges found: {sorted(fusions)}). An anchor is "
            "declared with `&name` and merged with `<<: *name`."
        ),
        fr=(
            f"Aucune ancre YAML n'est fusionnée dans le fichier (ancres "
            f"trouvées : {sorted(ancres)}, fusions trouvées : "
            f"{sorted(fusions)}). Une ancre se déclare par `&nom` et se "
            "fusionne par `<<: *nom`."
        ),
    )
    assert fusions & ancres, message(
        en=(
            f"The merged anchors {sorted(fusions)} do not match the declared "
            f"ones {sorted(ancres)}."
        ),
        fr=(
            f"Les ancres fusionnées {sorted(fusions)} ne correspondent pas aux "
            f"ancres déclarées {sorted(ancres)}."
        ),
    )

    # LA MOITIE QUI COMPTE LE PLUS, ET ELLE EST ICI PLUTOT QUE DANS UN TEST
    # A ELLE. Une factorisation qui change le comportement n'est pas une
    # factorisation, c'est une regression. Mais ces exigences sont vraies
    # DES L'ETAT DE DEPART, ou le pipeline est deja sain : en faire un test
    # autonome le ferait passer avant tout travail, ce que
    # `valider-labs.py` refuse a juste titre. Le garde-fou rejoint donc le
    # test qui mesure le travail reel.
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch since your changes.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut depuis vos modifications.",
    )
    tous = jobs(forge, dernier["id"], projet_du_lab["id"])

    echoues = [
        j.get("name") for j in tous
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=(
            f"These jobs failed after the refactoring: {echoues}. A "
            "refactoring that changes behaviour is a regression."
        ),
        fr=(
            f"Ces jobs ont échoué après la factorisation : {echoues}. Une "
            "factorisation qui change le comportement est une régression."
        ),
    )

    reussis = [j for j in tous if j.get("status") == "success"]
    assert len(reussis) >= 4, message(
        en=(
            f"Only {len(reussis)} job(s) succeeded, four were expected. Did a "
            "job lose its stage, or its rules, along the way?"
        ),
        fr=(
            f"Seulement {len(reussis)} job(s) ont réussi, quatre étaient "
            "attendus. Un job aurait-il perdu son stage, ou ses règles, en "
            "route ?"
        ),
    )

    # Non-regression des acquis : la couverture remonte toujours (lab 10).
    detail = api(forge, f"/projects/{projet_du_lab['id']}/pipelines/{dernier['id']}")
    couverture = (detail or {}).get("coverage") if isinstance(detail, dict) else None
    des_jobs = []
    for j in reussis:
        d = api(forge, f"/projects/{projet_du_lab['id']}/jobs/{j['id']}")
        if isinstance(d, dict) and d.get("coverage") is not None:
            des_jobs.append(d["coverage"])
    assert couverture is not None or des_jobs, message(
        en=(
            "No coverage figure reaches GitLab any more. The `coverage:` "
            "expression was lost in the refactoring: it belongs to the job, and "
            "`extends` does not carry what the job no longer declares."
        ),
        fr=(
            "Aucun chiffre de couverture ne remonte plus à GitLab. "
            "L'expression `coverage:` a été perdue dans la factorisation : "
            "elle appartient au job, et `extends` ne transporte pas ce que le "
            "job ne déclare plus."
        ),
    )
