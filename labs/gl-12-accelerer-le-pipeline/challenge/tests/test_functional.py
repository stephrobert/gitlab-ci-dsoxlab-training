"""Tests du lab gl-12-accelerer-le-pipeline.

DEUX GASPILLAGES, DEUX MESURES REELLEMENT OBSERVABLES. C'est ce qui rend ce lab
mesurable alors que son sujet, « aller plus vite », ne l'est pas directement :
on ne note pas une duree, qui varie avec la charge de la machine, on note les
deux mecaniques qui la font baisser.

LE PREMIER GASPILLAGE EST LE PLUS SOURNOIS, ET IL FAUT LE DIRE EXACTEMENT.
La cle du cache vaut `$CI_COMMIT_SHA`. Mesure du 2026-10-22 : le cache est
alors bel et bien RESTAURE, parce que les deux jobs d'un MEME pipeline
partagent ce SHA, donc cette cle. Le second retrouve le cache du premier.

Ce que cette cle rend impossible, c'est la reutilisation d'un pipeline AU
SUIVANT : le SHA change a chaque commit, et le cache du passage precedent
existe sous un nom que personne ne cherchera plus. Il est cree, stocke,
facture en espace disque, et relu une seule fois.

Le test ne mesure donc pas une restauration, qui a lieu des l'etat de depart,
mais la STABILITE DE LA CLE d'un pipeline a l'autre. Elle se lit dans les
journaux, ou GitLab Runner ecrit « Checking cache for <cle>... », et elle ne
demande pas de lire le fichier de l'apprenant.

LE SECOND SE LIT DANS LE TEMPS. Deux jobs liberes de leur stage par `needs:`
se CHEVAUCHENT : l'un demarre avant que l'autre ne finisse. Les horodatages des
jobs le disent, et c'est une preuve directe, pas une lecture du fichier.

CE QUI RENDAIT CE LAB IMPOSSIBLE A MESURER, ET QUI A ETE CORRIGE : le runner
etait configure avec `concurrent = 1`. Deux jobs ne pouvaient alors jamais se
chevaucher, quoi qu'autorise leur `needs:`, et la duree du pipeline ne bougeait
pas d'une seconde. Le socle pose desormais `concurrent = 3`.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
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
    return {"projet": p, "pipeline": dernier, "jobs": jobs(forge, dernier["id"], p["id"])}


def _instant(valeur):
    """Lit un horodatage de l'API, ou None.

    GitLab les rend en ISO 8601 avec fuseau. Un job jamais demarre porte
    `null` : le distinguer d'une date compte, l'un disant « pas demarre » et
    l'autre « demarre a telle heure ».
    """
    if not valeur:
        return None
    try:
        return datetime.fromisoformat(str(valeur).replace("Z", "+00:00"))
    except ValueError:
        return None


def test_la_cle_du_cache_est_stable_entre_deux_pipelines(forge, contexte):
    """LA MESURE JUSTE : la cle ne doit plus changer d'un pipeline a l'autre.

    Avec `$CI_COMMIT_SHA`, le cache est restaure DANS un pipeline, les deux
    jobs partageant le meme SHA, mais jamais d'un pipeline au suivant. Mesurer
    une restauration ferait donc passer ce test sur l'etat de depart, ce que
    `valider-labs.py` a refuse a juste titre.

    On compare donc les cles que GitLab Runner inscrit dans les journaux de
    DEUX pipelines : identiques, le cache traverse les commits ; differentes,
    il est jete a chaque fois.

    Ce test porte aussi l'exigence qu'aucun job n'ait echoue : elle est vraie
    des l'etat de depart, donc elle ne peut pas faire un test a elle seule.
    """
    pipelines = api(
        forge,
        f"/projects/{contexte['projet']['id']}/pipelines",
        "ref=" + (contexte["projet"].get("default_branch") or "main")
        + "&per_page=10&order_by=id&sort=desc",
    )
    assert isinstance(pipelines, list) and len(pipelines) >= 2, message(
        en=(
            "Only one pipeline ran on the default branch. A cache key can only "
            "be compared across two runs: push again after your fix."
        ),
        fr=(
            "Un seul pipeline a tourné sur la branche par défaut. Une clé de "
            "cache ne se compare qu'entre deux passages : poussez à nouveau "
            "après votre correction."
        ),
    )

    def cles_du_pipeline(pipeline_id: int) -> set[str]:
        """Les cles de cache que le runner a inscrites dans les journaux."""
        trouvees: set[str] = set()
        for j in jobs(forge, pipeline_id, contexte["projet"]["id"]):
            brut = api(
                forge,
                f"/projects/{contexte['projet']['id']}/jobs/{j['id']}/trace",
                brut=True,
            )
            for m in re.finditer(r"checking cache for ([^\s.]+)", (brut or "").lower()):
                trouvees.add(m.group(1))
        return trouvees

    recentes = cles_du_pipeline(pipelines[0]["id"])
    precedentes = cles_du_pipeline(pipelines[1]["id"])

    assert recentes and precedentes, message(
        en=(
            "No cache key appears in the job logs of the two latest pipelines "
            f"(found: {sorted(recentes)} and {sorted(precedentes)}). Without a "
            "declared cache, nothing is kept from one run to the next."
        ),
        fr=(
            "Aucune clé de cache n'apparaît dans les journaux des deux "
            f"derniers pipelines (relevé : {sorted(recentes)} et "
            f"{sorted(precedentes)}). Sans cache déclaré, rien n'est conservé "
            "d'un passage à l'autre."
        ),
    )

    communes = recentes & precedentes
    assert communes, message(
        en=(
            "The cache keys differ between the two latest pipelines: "
            f"{sorted(recentes)} versus {sorted(precedentes)}. A key that "
            "changes on every commit makes the previous cache unfindable: it "
            "is created, stored, and never read again."
        ),
        fr=(
            "Les clés de cache diffèrent entre les deux derniers pipelines : "
            f"{sorted(recentes)} contre {sorted(precedentes)}. Une clé qui "
            "change à chaque commit rend le cache précédent introuvable : il "
            "est créé, stocké, et jamais relu."
        ),
    )

    echoues = [
        j.get("name") for j in contexte["jobs"]
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=f"These jobs failed in the latest pipeline: {echoues}.",
        fr=f"Ces jobs ont échoué dans le dernier pipeline : {echoues}.",
    )


def test_deux_jobs_se_chevauchent_dans_le_temps(contexte):
    """LA PREUVE DU PARALLELISME, lue dans les horodatages.

    Deux jobs liberes de leur stage par `needs:` se chevauchent : l'un demarre
    avant que l'autre ne finisse. C'est une preuve directe, et la seule qui ne
    passe pas par la lecture du fichier : l'API n'expose pas les `needs:`.

    On compare des jobs de STAGES DIFFERENTS. Deux jobs d'un meme stage
    tournent ensemble sans que personne ait rien decide : ce serait mesurer le
    comportement par defaut de GitLab, pas le travail de l'apprenant.
    """
    periodes = []
    for j in contexte["jobs"]:
        debut = _instant(j.get("started_at"))
        fin = _instant(j.get("finished_at"))
        if debut and fin and j.get("stage"):
            periodes.append((j.get("name"), j.get("stage"), debut, fin))

    assert len(periodes) >= 2, message(
        en=(
            f"Only {len(periodes)} job(s) have both a start and an end time: "
            "there is nothing to compare."
        ),
        fr=(
            f"Seulement {len(periodes)} job(s) portent une heure de début et de "
            "fin : il n'y a rien à comparer."
        ),
    )

    chevauchements = []
    for i, (n1, s1, d1, f1) in enumerate(periodes):
        for n2, s2, d2, f2 in periodes[i + 1:]:
            if s1 == s2:
                continue
            if d1 < f2 and d2 < f1:
                chevauchements.append(f"{n1} [{s1}] / {n2} [{s2}]")

    assert chevauchements, message(
        en=(
            "No two jobs from different stages overlapped in time. Stages run "
            "one after another by default: a job has to be freed from that "
            "order to start earlier. Jobs seen: "
            + ", ".join(f"{n} [{s}]" for n, s, _, _ in periodes)
        ),
        fr=(
            "Aucun couple de jobs de stages différents ne s'est chevauché dans "
            "le temps. Les stages s'enchaînent l'un après l'autre par défaut : "
            "un job doit être libéré de cet ordre pour démarrer plus tôt. Jobs "
            "relevés : "
            + ", ".join(f"{n} [{s}]" for n, s, _, _ in periodes)
        ),
    )
