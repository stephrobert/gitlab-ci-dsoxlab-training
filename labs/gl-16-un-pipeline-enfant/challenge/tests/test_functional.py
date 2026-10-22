"""Tests du lab gl-16-un-pipeline-enfant.

UN PIPELINE ENFANT SE MESURE PAR UN ENDPOINT A LUI. GitLab appelle « bridge »
le job qui declenche un pipeline aval, et il l'expose sur
`/pipelines/:id/bridges`, avec le pipeline declenche dans
`downstream_pipeline`. Ce n'est donc pas un job comme les autres, et le
chercher dans la liste des jobs ne donnerait rien.

Les deux tests portent sur ce que le serveur a produit :

- UN PIPELINE ENFANT EXISTE, declenche par un job du parent, et il a reussi.
  Un enfant qui n'existe pas ne se signale pas : le parent passe au vert sans
  lui ;
- LE PARENT ATTEND SON ENFANT. C'est la moitie qui compte : sans `strategy:`,
  le parent declenche l'enfant et passe au vert sans se soucier du resultat.
  On verifie donc que le job declencheur porte l'etat de l'enfant.

LA STRATEGIE RECOMMANDEE EST `mirror`, ET CE N'EST PAS UN DETAIL DE
VOCABULAIRE. `depend` compte comme REUSSI un pipeline aval en echec dont un job
porte `allow_failure: true` : il masque donc exactement ce qu'on lui demande de
surveiller. GitLab le qualifie de « not recommended, use mirror instead », et
`mirror` existe depuis la 18.2. L'instance du lab tourne en 19.5.1 : il est
disponible, et le corrige s'en sert.
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
def contexte(forge):
    p = projet(forge)
    assert p is not None, message(
        en="The pipeline-craft project was not found on the lab GitLab instance.",
        fr="Le projet pipeline-craft n'a pas été trouvé sur le GitLab du lab.",
    )
    dernier = dernier_pipeline(forge, p.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut.",
    )
    ponts = api(forge, f"/projects/{p['id']}/pipelines/{dernier['id']}/bridges")
    return {
        "projet": p,
        "pipeline": dernier,
        "jobs": jobs(forge, dernier["id"], p["id"]),
        "ponts": ponts if isinstance(ponts, list) else [],
    }


def test_un_pipeline_enfant_a_tourne(contexte):
    """Un pipeline enfant existe, et il a reussi.

    Le job qui declenche un pipeline aval n'est pas un job ordinaire : GitLab
    l'appelle « bridge » et le sert sur un endpoint a part. Son champ
    `downstream_pipeline` porte l'enfant.
    """
    ponts = contexte["ponts"]
    assert ponts, message(
        en=(
            "No trigger job in the latest pipeline. A job that starts a "
            "downstream pipeline carries a `trigger:` key, and GitLab serves "
            "it on /pipelines/:id/bridges, not among the ordinary jobs."
        ),
        fr=(
            "Aucun job de déclenchement dans le dernier pipeline. Un job qui "
            "lance un pipeline aval porte une clé `trigger:`, et GitLab le "
            "sert sur /pipelines/:id/bridges, pas parmi les jobs ordinaires."
        ),
    )

    enfants = [
        p.get("downstream_pipeline") for p in ponts
        if isinstance(p.get("downstream_pipeline"), dict)
    ]
    assert enfants, message(
        en=(
            f"The {len(ponts)} trigger job(s) started no downstream pipeline. "
            "A `trigger:` that includes nothing runnable creates no child."
        ),
        fr=(
            f"Les {len(ponts)} job(s) de déclenchement n'ont lancé aucun "
            "pipeline aval. Un `trigger:` qui n'inclut rien d'exécutable ne "
            "crée pas d'enfant."
        ),
    )

    statuts = [e.get("status") for e in enfants]
    assert any(s == "success" for s in statuts), message(
        en=f"No child pipeline succeeded (statuses: {statuts}).",
        fr=f"Aucun pipeline enfant n'a réussi (statuts : {statuts}).",
    )


def test_le_parent_attend_le_resultat_de_son_enfant(contexte):
    """LA MOITIE QUI COMPTE : un enfant ignore ne sert a rien.

    Sans `strategy:`, le job declencheur passe au vert des que l'enfant est
    LANCE, sans attendre son resultat. Le parent est alors vert quoi qu'il
    arrive en aval, et le pipeline enfant devient decoratif.

    On compare donc l'etat du job declencheur a celui de son enfant : s'ils
    concordent, le parent attend et reflete. On accepte `mirror` comme
    `depend`, le lab mesurant le comportement et non le mot-cle, mais le
    corrige utilise `mirror` : `depend` compte comme reussi un enfant en echec
    dont un job porte `allow_failure: true`.

    Ce test porte aussi les garde-fous habituels, vrais des l'etat de depart.
    """
    ponts = contexte["ponts"]
    assert ponts, message(
        en="No trigger job in the latest pipeline.",
        fr="Aucun job de déclenchement dans le dernier pipeline.",
    )

    concordants = []
    for p in ponts:
        enfant = p.get("downstream_pipeline")
        if not isinstance(enfant, dict):
            continue
        concordants.append(
            (p.get("name"), p.get("status"), enfant.get("status"))
        )

    assert concordants, message(
        en="No trigger job carries a downstream pipeline to compare with.",
        fr="Aucun job de déclenchement ne porte de pipeline aval à comparer.",
    )

    accordes = [
        (n, sp, se) for n, sp, se in concordants
        if sp == se or (sp == "success" and se == "success")
    ]
    assert accordes, message(
        en=(
            "The trigger job's status does not reflect its child's: "
            + ", ".join(f"{n}: {sp} / child {se}" for n, sp, se in concordants)
            + ". Without a `strategy:`, the parent goes green as soon as the "
            "child is started, whatever happens next."
        ),
        fr=(
            "L'état du job de déclenchement ne reflète pas celui de son "
            "enfant : "
            + ", ".join(f"{n} : {sp} / enfant {se}" for n, sp, se in concordants)
            + ". Sans `strategy:`, le parent passe au vert dès que l'enfant "
            "est lancé, quoi qu'il advienne ensuite."
        ),
    )

    echoues = [
        j.get("name") for j in contexte["jobs"]
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=f"These jobs failed in the parent pipeline: {echoues}.",
        fr=f"Ces jobs ont échoué dans le pipeline parent : {echoues}.",
    )
