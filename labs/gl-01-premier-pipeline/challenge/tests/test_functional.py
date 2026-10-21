"""Tests du lab gl-01-premier-pipeline.

ON NOTE L'ETAT LAISSE SUR LA FORGE, pas les commandes tapees :

- un pipeline a reellement tourne sur la branche par defaut ;
- il est vert ;
- il porte au moins trois jobs reussis, repartis sur plusieurs stages ;
- ces jobs couvrent les trois gestes promis : controle du style, tests, build.

CE QU'ON NE VERIFIE PAS, ET C'EST VOULU. Ni le nom des jobs, ni le nom des
stages, ni le contenu du `.gitlab-ci.yml`. Un apprenant qui nomme ses jobs
autrement, ou qui met le lint et les tests dans le meme stage, a quand meme
fait le travail. Lire le fichier reviendrait a noter l'intention, et a refuser
une solution correcte parce qu'elle n'est pas la notre.

LE PIEGE QUE CES TESTS EVITENT : un pipeline vert qui ne fait rien. Un
`.gitlab-ci.yml` avec un seul job `echo ok` passe au vert et ne prouve rien.
D'ou l'exigence de trois jobs reussis couvrant trois gestes distincts, deduits
du journal des jobs et non de leur nom.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    dernier_pipeline,
    forge_joignable,
    jobs,
    projet,
    stages,
)

from conftest import lab_host, message  # noqa: E402


@pytest.fixture(scope="module")
def host():
    return lab_host(HOTE)


@pytest.fixture(scope="module")
def forge(host):
    """Garde-fou : sans forge joignable, aucun test ne mesure l'apprenant.

    GitLab met plusieurs minutes a repondre au premier demarrage. Sans ce
    garde-fou, tous les tests echoueraient et l'apprenant chercherait une faute
    qu'il n'a pas commise.
    """
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
def pipeline(forge):
    p = projet(forge)
    assert p is not None, message(
        en="The pipeline-craft project was not found on the lab GitLab instance.",
        fr="Le projet pipeline-craft n'a pas été trouvé sur le GitLab du lab.",
    )
    dernier = dernier_pipeline(forge, p.get("default_branch") or "main")
    assert dernier is not None, message(
        en=(
            "No pipeline has ever run on the default branch. A .gitlab-ci.yml "
            "committed but never pushed does not create one."
        ),
        fr=(
            "Aucun pipeline n'a jamais tourné sur la branche par défaut. Un "
            ".gitlab-ci.yml commité mais non poussé n'en crée pas."
        ),
    )
    return {"projet": p, "pipeline": dernier}


def test_le_pipeline_est_vert(pipeline):
    statut = pipeline["pipeline"].get("status")
    assert statut == "success", message(
        en=f"The latest pipeline on the default branch is '{statut}', not 'success'.",
        fr=f"Le dernier pipeline de la branche par défaut est « {statut} », pas « success ».",
    )


def test_trois_jobs_au_moins_ont_reussi(forge, pipeline):
    tous = jobs(forge, pipeline["pipeline"]["id"], pipeline["projet"]["id"])
    reussis = [j for j in tous if j.get("status") == "success"]
    assert len(reussis) >= 3, message(
        en=(
            f"The pipeline has {len(reussis)} successful job(s), three are expected: "
            "one green job that does nothing proves nothing."
        ),
        fr=(
            f"Le pipeline compte {len(reussis)} job(s) réussi(s), trois sont attendus : "
            "un seul job vert qui ne fait rien ne prouve rien."
        ),
    )


def test_les_etapes_sont_visibles(forge, pipeline):
    tous = jobs(forge, pipeline["pipeline"]["id"], pipeline["projet"]["id"])
    presents = stages(tous)
    assert len(presents) >= 2, message(
        en=(
            f"All jobs sit in a single stage ({sorted(presents)}). The pipeline "
            "should show its steps as separate stages."
        ),
        fr=(
            f"Tous les jobs sont dans un seul stage ({sorted(presents)}). Le "
            "pipeline doit montrer ses étapes comme des stages distincts."
        ),
    )


def test_les_trois_gestes_ont_ete_faits(forge, pipeline):
    """Les trois gestes se lisent dans le JOURNAL des jobs, pas dans leur nom.

    Un apprenant est libre de nommer `verifier` son job de lint. Ce qui compte
    est que la commande ait tourne, et le journal du job en porte la trace.
    """
    tous = jobs(forge, pipeline["pipeline"]["id"], pipeline["projet"]["id"])
    reussis = [j for j in tous if j.get("status") == "success"]

    traces = ""
    for j in reussis:
        r = forge.run(
            'JETON=$(cat /etc/dsoxlab/jeton-api 2>/dev/null); '
            f'curl -sS --max-time 20 -H "PRIVATE-TOKEN: $JETON" '
            f'http://gitlab-1.lab/api/v4/projects/{pipeline["projet"]["id"]}'
            f'/jobs/{j["id"]}/trace'
        )
        if r.rc == 0:
            traces += r.stdout.lower()

    gestes = {
        "lint": ("lint", "ruff", "flake8", "black"),
        "tests": ("pytest", "make test", "test session"),
        "build": ("docker build", "make build", "podman build", "buildah"),
    }
    manquants = [
        nom for nom, motifs in gestes.items()
        if not any(m in traces for m in motifs)
    ]
    assert not manquants, message(
        en=(
            f"No trace of these steps in the job logs: {manquants}. The pipeline "
            "is green, but it did not do what the mission asked."
        ),
        fr=(
            f"Aucune trace de ces étapes dans les journaux des jobs : {manquants}. "
            "Le pipeline est vert, mais il n'a pas fait ce que la mission demandait."
        ),
    )
