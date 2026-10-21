"""Tests du lab gl-06-controler-execution.

CE LAB POSE UN PROBLEME DE MESURE QU'IL FAUT DIRE FRANCHEMENT. Trois des
quatre exigences s'observent dans l'etat du pipeline, et la quatrieme, le
`workflow:` global, ne s'observe qu'en POUSSANT sur une branche qui ne doit
rien declencher. Un test n'a pas a modifier l'etat du lab : il le mesure.

Le quatrieme test lit donc la CONFIGURATION FUSIONNEE que GitLab a comprise,
celle que son propre linter rend sur `/ci/lint`. Ce n'est pas la lecture du
fichier de l'apprenant : c'est ce que le serveur en a fait, apres resolution
des inclusions et des ancres. C'est le plus proche de l'etat observable que ce
lab permette, et c'est assume plutot que masque.

CE QUE LES DEUX AUTRES MESURENT, dans l'etat laisse sur la forge :

- un job de deploiement a REUSSI automatiquement sur la branche par defaut, et
  le pipeline est reste vert. Les deux exigences tiennent dans le meme test, et
  ce n'est pas de la paresse : ce lab part d'un pipeline DEJA VERT, donc un
  test du seul vert passerait avant tout travail ;
- un autre job de deploiement attend une DECISION HUMAINE : il est en statut
  `manual`, donc declarable et non lance. C'est la difference entre deployer
  en recette et deployer en production.

CE QU'ON NE VERIFIE PAS : le nom des jobs ni celui du stage. Un job de
deploiement se reconnait a ce qu'il fait, pas a son intitule.
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
    tous = jobs(forge, dernier["id"], p["id"])
    return {"projet": p, "pipeline": dernier, "jobs": tous}


@pytest.fixture(scope="module")
def deploiements(forge, contexte) -> list[dict]:
    """Les jobs qui DEPLOIENT, reconnus par leur stage, leur nom ou leur journal.

    On ne se fie pas au seul nom : un apprenant peut appeler son job `livrer`.
    Un job de deploiement se reconnait a ce qu'il execute, et le depot fil
    rouge fournit pour cela `scripts/deploy-demo.sh`.

    Le journal d'un job `manual` est vide, puisqu'il n'a pas tourne : c'est
    justement pourquoi le stage et le nom comptent aussi. Un test qui
    n'aurait regarde que les journaux n'aurait jamais trouve le job manuel.
    """
    trouves = []
    for j in contexte["jobs"]:
        indices = [(j.get("stage") or "").lower(), (j.get("name") or "").lower()]
        if j.get("status") not in (None, "manual", "created", "skipped"):
            brut = api(
                forge,
                f"/projects/{contexte['projet']['id']}/jobs/{j['id']}/trace",
                brut=True,
            )
            if brut:
                indices.append(brut.lower())
        if any("deploy" in i or "deploi" in i for i in indices):
            trouves.append(j)
    return trouves


def test_un_deploiement_automatique_a_reussi(contexte, deploiements):
    """Un deploiement part tout seul quand la branche par defaut bouge.

    IL N'Y A PAS DE TEST « LE PIPELINE EST VERT » DANS CE LAB, et c'est une
    correction, pas un oubli. Ce lab part d'un pipeline DEJA VERT : un tel test
    passait donc avant tout travail, ce que `valider-labs.py` a refuse. Le vert
    est donc exige ici, par un test qui mesure quelque chose que l'etat de
    depart ne porte pas. A noter : un job manuel en attente ne rend PAS un
    pipeline rouge, donc un pipeline rouge signale un vrai probleme.
    """
    statut = contexte["pipeline"].get("status")
    assert statut == "success", message(
        en=(
            f"The latest pipeline on the default branch is '{statut}', not "
            "'success'. A pending manual job does not make a pipeline red: "
            "something else is failing."
        ),
        fr=(
            f"Le dernier pipeline de la branche par défaut est « {statut} », "
            "pas « success ». Un job manuel en attente ne rend pas un pipeline "
            "rouge : autre chose échoue."
        ),
    )
    reussis = [j for j in deploiements if j.get("status") == "success"]
    assert reussis, message(
        en=(
            "No deployment job succeeded on the default branch. One "
            "environment should be deployed automatically when the default "
            "branch moves."
        ),
        fr=(
            "Aucun job de déploiement n'a réussi sur la branche par défaut. Un "
            "environnement doit être déployé automatiquement quand la branche "
            "par défaut bouge."
        ),
    )


def test_un_deploiement_attend_une_decision_humaine(deploiements):
    """Un job `manual` n'a pas tourne, et c'est exactement ce qu'on veut.

    Deployer en production ne se declenche pas sur un push : quelqu'un
    l'autorise. GitLab marque un tel job `manual` tant que personne ne l'a
    lance.
    """
    manuels = [j for j in deploiements if j.get("status") == "manual"]
    assert manuels, message(
        en=(
            "No deployment job is waiting for a human decision. One of them "
            "should be `when: manual`: deploying to production is a decision, "
            "not a consequence of a push."
        ),
        fr=(
            "Aucun job de déploiement n'attend une décision humaine. L'un "
            "d'eux doit être `when: manual` : déployer en production est une "
            "décision, pas la conséquence d'un push."
        ),
    )


def test_un_workflow_global_decide_quand_le_pipeline_demarre(forge, contexte):
    """La seule exigence qui ne s'observe pas dans l'etat du pipeline.

    Un `workflow:` decide si le pipeline NAIT. Son effet ne se voit qu'en
    poussant sur une branche qui ne doit rien declencher, ce qu'un test n'a pas
    a faire. On lit donc la configuration fusionnee que GitLab a comprise, et
    on le dit : c'est une lecture de configuration, pas d'etat.
    """
    rapport = lint_configuration(forge, contexte["projet"]["id"])
    assert rapport is not None, message(
        en="GitLab's CI linter did not answer; the configuration could not be checked.",
        fr="Le linter CI de GitLab n'a pas répondu : la configuration n'a pas pu être vérifiée.",
    )
    assert rapport.get("valid") is True, message(
        en=f"GitLab refuses the configuration: {rapport.get('errors')}",
        fr=f"GitLab refuse la configuration : {rapport.get('errors')}",
    )
    fusionne = (rapport.get("merged_yaml") or "").lower()
    assert fusionne, message(
        en="GitLab did not return the merged configuration.",
        fr="GitLab n'a pas rendu la configuration fusionnée.",
    )
    assert "workflow" in fusionne, message(
        en=(
            "The merged configuration carries no `workflow:` block. Without "
            "it, a pipeline is born on every push, on every branch, including "
            "the ones nobody is watching."
        ),
        fr=(
            "La configuration fusionnée ne porte aucun bloc `workflow:`. Sans "
            "lui, un pipeline naît à chaque push, sur chaque branche, y "
            "compris celles que personne ne regarde."
        ),
    )
