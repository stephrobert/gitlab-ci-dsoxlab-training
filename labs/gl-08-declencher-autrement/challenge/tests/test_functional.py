"""Tests du lab gl-08-declencher-autrement.

CE QUE CE LAB MESURE, et c'est plus riche que les precedents : un pipeline ne
naît pas que d'un push. Il peut naître d'une planification, d'un appel a l'API,
d'un jeton de declenchement, et un job peut vouloir ne tourner que pour
certaines de ces sources.

Les quatre tests portent sur l'etat laisse sur la forge :

- une PLANIFICATION existe et est active. Elle ne se devine pas : elle se cree,
  avec sa frequence et sa reference ;
- un JETON DE DECLENCHEMENT existe. C'est lui qui permet a un systeme tiers de
  lancer le pipeline sans compte ni cle SSH ;
- un pipeline a reellement tourne avec une source AUTRE QUE `push`, et aucun de
  ses jobs n'a echoue. Sans cela, le `workflow:` aurait beau accepter ces
  sources, rien ne prouverait qu'elles passent ;
- un job est RESERVE a une source : il apparait dans le pipeline hors push, et
  pas dans celui du push. C'est la preuve que `CI_PIPELINE_SOURCE` est comprise,
  et c'est la seule facon de le montrer sans lire le fichier.

CE QU'ON NE LIT JAMAIS : la valeur d'un jeton de declenchement. L'API la rend,
et un message d'echec qui la porterait la publierait dans la sortie du
`dsoxlab check`. On ne lit que son existence et sa description.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    api,
    forge_joignable,
    jobs,
    noms,
    projet,
)

from conftest import lab_host, message  # noqa: E402

# Les sources qui ne sont pas un push. `web` en fait partie : un pipeline lance
# depuis le bouton « Run pipeline » de l'interface compte comme un
# declenchement manuel, et le lab l'accepte.
HORS_PUSH = ("schedule", "trigger", "api", "web", "pipeline")


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


@pytest.fixture(scope="module")
def pipelines_par_source(forge, projet_du_lab):
    """Les pipelines du projet, groupes par source.

    Un seul relevé pour les quatre tests, et il porte sur TOUTES les branches :
    un pipeline de planification peut viser une autre reference que la branche
    par defaut.
    """
    tous = api(
        forge,
        f"/projects/{projet_du_lab['id']}/pipelines",
        "per_page=50&order_by=id&sort=desc",
    )
    groupes: dict[str, list] = {}
    if isinstance(tous, list):
        for p in tous:
            groupes.setdefault(p.get("source") or "inconnue", []).append(p)
    return groupes


def test_une_planification_existe_et_est_active(forge, projet_du_lab):
    plans = api(forge, f"/projects/{projet_du_lab['id']}/pipeline_schedules")
    assert isinstance(plans, list), message(
        en="The project's pipeline schedules could not be read.",
        fr="Les planifications de pipeline du projet n'ont pas pu être lues.",
    )
    actives = [p for p in plans if p.get("active")]
    assert actives, message(
        en=(
            f"The project has {len(plans)} schedule(s), none of them active. A "
            "nightly run that nobody scheduled never happens."
        ),
        fr=(
            f"Le projet compte {len(plans)} planification(s), aucune active. "
            "Une exécution nocturne que personne n'a planifiée n'arrive jamais."
        ),
    )


def test_un_jeton_de_declenchement_existe(forge, projet_du_lab):
    """On lit son EXISTENCE, jamais sa valeur.

    L'API rend le jeton en clair. Un message d'echec qui le porterait le
    publierait dans la sortie du `dsoxlab check`, et un journal se telecharge.
    """
    jetons = api(forge, f"/projects/{projet_du_lab['id']}/triggers")
    assert isinstance(jetons, list), message(
        en="The project's trigger tokens could not be read.",
        fr="Les jetons de déclenchement du projet n'ont pas pu être lus.",
    )
    assert jetons, message(
        en=(
            "The project has no trigger token. Without one, no third-party "
            "system can start the pipeline: it would need an account, or a key."
        ),
        fr=(
            "Le projet n'a aucun jeton de déclenchement. Sans lui, aucun "
            "système tiers ne peut lancer le pipeline : il lui faudrait un "
            "compte, ou une clé."
        ),
    )


def test_un_pipeline_est_ne_hors_push(forge, projet_du_lab, pipelines_par_source):
    """Le `workflow:` peut accepter une source : encore faut-il qu'elle passe.

    Ce test ferme l'ecart entre la configuration et le fait. Il verifie aussi
    qu'aucun job de ce pipeline n'a echoue : un declenchement qui aboutit a un
    pipeline rouge ne prouve que la moitie du chemin.
    """
    trouves = {s: p for s, p in pipelines_par_source.items() if s in HORS_PUSH}
    assert trouves, message(
        en=(
            f"No pipeline ran from a source other than a push. Sources seen: "
            f"{sorted(pipelines_par_source)}. A `workflow:` that accepts a "
            "source proves nothing until a pipeline actually ran from it."
        ),
        fr=(
            f"Aucun pipeline n'a tourné depuis une source autre qu'un push. "
            f"Sources relevées : {sorted(pipelines_par_source)}. Un "
            "`workflow:` qui accepte une source ne prouve rien tant qu'aucun "
            "pipeline n'en est né."
        ),
    )

    source, liste = next(iter(trouves.items()))
    recent = liste[0]
    tous = jobs(forge, recent["id"], projet_du_lab["id"])
    echoues = [
        j.get("name") for j in tous
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=(
            f"The pipeline triggered from '{source}' has failed job(s): "
            f"{echoues}."
        ),
        fr=(
            f"Le pipeline déclenché depuis « {source} » porte des jobs en "
            f"échec : {echoues}."
        ),
    )


def test_un_job_est_reserve_a_une_source(forge, projet_du_lab, pipelines_par_source):
    """LA PREUVE QUE `CI_PIPELINE_SOURCE` EST COMPRISE.

    Un job reserve a une source apparait dans le pipeline de cette source et
    PAS dans celui d'un push. Comparer les deux listes de jobs est la seule
    facon de le montrer sans lire le fichier de l'apprenant : les regles d'un
    job ne sont pas exposees par l'API.
    """
    hors = [s for s in pipelines_par_source if s in HORS_PUSH]
    assert hors, message(
        en="No pipeline ran from a source other than a push, so nothing can be compared.",
        fr="Aucun pipeline hors push n'a tourné : il n'y a rien à comparer.",
    )
    assert "push" in pipelines_par_source, message(
        en=(
            "No pipeline ran from a push, so the comparison cannot be made. "
            "Push a commit to the default branch as well."
        ),
        fr=(
            "Aucun pipeline n'a tourné depuis un push : la comparaison est "
            "impossible. Poussez aussi un commit sur la branche par défaut."
        ),
    )

    jobs_hors: set[str] = set()
    for source in hors:
        recent = pipelines_par_source[source][0]
        jobs_hors |= noms(jobs(forge, recent["id"], projet_du_lab["id"]))

    recent_push = pipelines_par_source["push"][0]
    jobs_push = noms(jobs(forge, recent_push["id"], projet_du_lab["id"]))

    reserves = jobs_hors - jobs_push
    assert reserves, message(
        en=(
            "Every job of the non-push pipeline also runs on a push "
            f"({sorted(jobs_hors)}). One job should be reserved to a source, "
            "through a rule on `$CI_PIPELINE_SOURCE`."
        ),
        fr=(
            "Tous les jobs du pipeline hors push tournent aussi sur un push "
            f"({sorted(jobs_hors)}). Un job devrait être réservé à une source, "
            "par une règle sur `$CI_PIPELINE_SOURCE`."
        ),
    )
