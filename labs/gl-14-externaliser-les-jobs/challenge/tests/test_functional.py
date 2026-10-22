"""Tests du lab gl-14-externaliser-les-jobs.

CE LAB RETROUVE LA MESURE PAR L'ETAT, et c'est une difference nette avec le
precedent. Au lab 13, la factorisation par `extends` et par ancres etait
resolue dans le YAML avant que GitLab ne la voie : il fallait lire le fichier.
Ici, GitLab SAIT qu'il a inclus des fichiers, et il le dit : son linter rend la
liste des inclusions a cote de la configuration fusionnee.

UN SEUL TEST, parce qu'une seule chose change vraiment. Il verifie que GitLab
a bien INCLUS plusieurs fichiers, qu'il nomme lui-meme, puis il ajoute deux
garde-fous : le comportement n'a pas bouge (les jobs tournent, aucun n'echoue,
la couverture remonte), et l'orchestrateur garde ce qui tient le pipeline
ensemble (les stages, le workflow).

Ces deux garde-fous sont vrais DES L'ETAT DE DEPART. Ils ne peuvent donc pas
faire des tests a eux seuls, et ils s'ajoutent a celui qui mesure le travail.
C'est la meme regle qu'au lab 13, et c'est `valider-labs.py` qui la tient :
un test vert sur l'etat de depart n'est pas un test.
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
    lint_configuration,
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


def test_gitlab_a_inclus_plusieurs_fichiers(forge, projet_du_lab):
    """GitLab nomme lui-meme les fichiers qu'il a inclus.

    C'est la difference avec le lab precedent : une inclusion n'est pas
    resolue dans le YAML, elle est faite PAR GitLab, qui en garde donc la
    trace. Son linter rend la liste a cote de la configuration fusionnee, ce
    qui evite de lire le fichier de l'apprenant.

    CE TEST PORTE AUSSI LA NON-REGRESSION, pour la meme raison qu'au lab 13 :
    les exigences de comportement sont vraies des l'etat de depart, ou le
    pipeline est deja sain, et un test autonome passerait avant tout travail.
    """
    rapport = lint_configuration(forge, projet_du_lab["id"])
    assert rapport is not None, message(
        en="GitLab's CI linter did not answer; the configuration could not be checked.",
        fr="Le linter CI de GitLab n'a pas répondu : la configuration n'a pas pu être vérifiée.",
    )
    assert rapport.get("valid") is True, message(
        en=f"GitLab refuses the configuration: {rapport.get('errors')}",
        fr=f"GitLab refuse la configuration : {rapport.get('errors')}",
    )

    inclus = rapport.get("includes") or []
    noms = []
    for i in inclus:
        if isinstance(i, dict):
            # Selon la version, la cle utile est `location`, `local` ou `raw`.
            noms.append(i.get("location") or i.get("local") or i.get("raw") or str(i))
        else:
            noms.append(str(i))

    assert len(noms) >= 2, message(
        en=(
            f"GitLab reports {len(noms)} included file(s): {noms}. The pipeline "
            "is still one block. An orchestrator keeps the stages, the "
            "workflow and the shared variables; the jobs move out."
        ),
        fr=(
            f"GitLab rapporte {len(noms)} fichier(s) inclus : {noms}. Le "
            "pipeline est encore d'un seul bloc. Un orchestrateur garde les "
            "stages, le workflow et les variables communes ; les jobs "
            "déménagent."
        ),
    )

    # --- Non-regression : le comportement n'a pas bouge --------------------
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
            f"These jobs failed after the split: {echoues}. A job that moved to "
            "another file keeps all its keys, or it is not the same job."
        ),
        fr=(
            f"Ces jobs ont échoué après le découpage : {echoues}. Un job qui "
            "déménage garde toutes ses clés, sinon ce n'est plus le même job."
        ),
    )

    reussis = [j for j in tous if j.get("status") == "success"]
    assert len(reussis) >= 4, message(
        en=(
            f"Only {len(reussis)} job(s) succeeded, four were expected. Did a "
            "job stay behind in a file nobody includes?"
        ),
        fr=(
            f"Seulement {len(reussis)} job(s) ont réussi, quatre étaient "
            "attendus. Un job serait-il resté dans un fichier que personne "
            "n'inclut ?"
        ),
    )

    detail = api(forge, f"/projects/{projet_du_lab['id']}/pipelines/{dernier['id']}")
    couverture = detail.get("coverage") if isinstance(detail, dict) else None
    des_jobs = [
        d.get("coverage")
        for j in reussis
        if isinstance(d := api(forge, f"/projects/{projet_du_lab['id']}/jobs/{j['id']}"), dict)
        and d.get("coverage") is not None
    ]
    assert couverture is not None or des_jobs, message(
        en=(
            "No coverage figure reaches GitLab any more. The `coverage:` "
            "expression travels with its job: it belongs to the job, not to "
            "the file that holds it."
        ),
        fr=(
            "Aucun chiffre de couverture ne remonte plus à GitLab. "
            "L'expression `coverage:` voyage avec son job : elle appartient au "
            "job, pas au fichier qui le contient."
        ),
    )

    # --- Ce qui NE doit PAS demenager, et c'est un garde-fou ---------------
    #
    # Un decoupage qui disperserait la liste des stages ou le `workflow:` dans
    # les fichiers inclus rendrait l'ordre du pipeline illisible : il faudrait
    # ouvrir quatre fichiers pour savoir quand un pipeline naît.
    #
    # Cette exigence est vraie DES L'ETAT DE DEPART, ou tout est dans le meme
    # fichier : elle ne peut donc pas faire un test a elle seule, et elle
    # s'ajoute ici. C'est la meme raison qu'au lab 13.
    fusionne = (rapport.get("merged_yaml") or "").lower()
    assert fusionne, message(
        en="GitLab did not return the merged configuration.",
        fr="GitLab n'a pas rendu la configuration fusionnée.",
    )
    for attendu, quoi in (
        ("stages:", "la liste des stages"),
        ("workflow:", "le bloc workflow"),
    ):
        assert attendu in fusionne, message(
            en=(
                f"The merged configuration no longer carries `{attendu}`. "
                "Splitting the jobs out must not lose what holds the pipeline "
                "together."
            ),
            fr=(
                f"La configuration fusionnée ne porte plus `{attendu}` "
                f"({quoi}). Sortir les jobs ne doit pas faire perdre ce qui "
                "tient le pipeline ensemble."
            ),
        )
