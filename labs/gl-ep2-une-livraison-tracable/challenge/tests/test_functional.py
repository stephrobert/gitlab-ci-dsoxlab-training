"""Tests de l'epreuve gl-ep2-une-livraison-tracable.

L'EPREUVE DE FIN DU NIVEAU c2. Le niveau s'appelle « Livrer », et une livraison
qu'on ne peut pas retracer n'a pas eu lieu du point de vue de l'equipe : six
mois plus tard, personne ne sait quelle version tourne ou, ni qui l'a decidee,
ni comment y revenir.

QUATRE TRACES MANQUENT, et aucun job n'echoue pour autant. C'est ce qui rend
l'enonce difficile : la chaine ne se plaint de rien.

  1. GitLab NE CONNAIT AUCUN ENVIRONNEMENT. La page des environnements du
     projet est vide, donc rien ne dit ce qui tourne en recette ni en
     production ;
  2. L'IMAGE NE SORT PAS DU RUNNER. Elle est construite, puis meurt avec le
     conteneur du job : aucun deploiement ne peut reposer sur elle ;
  3. UN JOB ATTEND UN RUNNER QUI N'EXISTE PAS. Il n'est pas en erreur, il est
     en attente, et le pipeline n'atteint donc jamais sa fin ;
  4. LA PRODUCTION PART SANS DECISION. Le moindre commit sur la branche par
     defaut la met a jour.

CE QUI EST NOTE RESTE UN ETAT, lu dans l'API : les environnements que la forge
porte, les deploiements qu'elle a enregistres, les etiquettes du registre, et
l'etat des jobs du dernier pipeline. Aucun test ne lit un fichier du depot, et
aucun n'impose un nom d'environnement ni une facon de proteger la production.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    api,
    forge_joignable,
    jobs,
    lint_configuration,
    pipelines,
    projet,
)

from conftest import lab_host, message  # noqa: E402

# Les etats d'un job qui n'a pas commence. Un job qui reste la empeche le
# pipeline d'atteindre un etat terminal.
EN_ATTENTE = ("created", "pending", "waiting_for_resource")


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
def pipeline_de_main(forge, projet_du_lab):
    tous = pipelines(forge, ref="main")
    assert tous, message(
        en="No pipeline on the default branch: push your configuration.",
        fr="Aucun pipeline sur la branche par défaut : poussez votre configuration.",
    )
    dernier = tous[0]
    return {"pipeline": dernier, "jobs": jobs(forge, dernier["id"], projet_du_lab["id"])}


@pytest.fixture(scope="module")
def configuration(forge, projet_du_lab):
    """Les jobs de `main` tels que GITLAB les a compiles."""
    rapport = lint_configuration(forge, projet_du_lab["id"], "main")
    assert rapport is not None, message(
        en="GitLab's CI linter did not answer for branch main.",
        fr="Le linter CI de GitLab n'a pas répondu pour la branche main.",
    )
    assert rapport.get("valid") is True, message(
        en=(
            "GitLab refuses the configuration of main:\n  "
            + "\n  ".join(rapport.get("errors") or ["(no reason given)"])
        ),
        fr=(
            "GitLab refuse la configuration de main :\n  "
            + "\n  ".join(rapport.get("errors") or ["(aucune raison donnée)"])
        ),
    )
    charge = yaml.safe_load(rapport["merged_yaml"])
    reserves = {
        "stages",
        "workflow",
        "default",
        "variables",
        "include",
        "image",
        "services",
        "before_script",
        "after_script",
        "cache",
    }
    return {
        nom: corps
        for nom, corps in charge.items()
        if isinstance(corps, dict) and nom not in reserves and not nom.startswith(".")
    }


def test_aucun_job_n_attend_un_runner_qui_n_existe_pas(pipeline_de_main):
    """TROISIEME TRACE, et elle passe en premier parce qu'elle bloque tout.

    Un job qui demande une etiquette qu'aucun runner ne porte n'echoue pas : il
    attend. Le pipeline reste donc en cours indefiniment, et tout ce qui vient
    apres lui n'arrive jamais. C'est la panne la plus desagreable de GitLab CI,
    parce qu'elle ne produit aucun message.

    Le test regarde les jobs du dernier pipeline de la branche par defaut :
    aucun ne doit etre en attente, et aucun ne doit avoir echoue.
    """
    attendent = {
        j.get("name"): j.get("status")
        for j in pipeline_de_main["jobs"]
        if j.get("status") in EN_ATTENTE
    }
    assert not attendent, message(
        en=(
            f"These jobs are still waiting to start: {attendent}. A job that "
            "asks for a runner tag no runner carries does not fail, it waits: "
            "the pipeline never reaches an end, and everything after that job "
            "never happens. Compare what the job asks for with what the "
            "project's runners offer."
        ),
        fr=(
            f"Ces jobs attendent encore de démarrer : {attendent}. Un job qui "
            "demande une étiquette de runner qu'aucun runner ne porte "
            "n'échoue pas, il attend : le pipeline n'atteint jamais sa fin, et "
            "tout ce qui vient après ce job n'arrive jamais. Comparez ce que "
            "le job demande avec ce que les runners du projet offrent."
        ),
    )

    echoues = [
        j.get("name") for j in pipeline_de_main["jobs"] if j.get("status") in ("failed",)
    ]
    assert not echoues, message(
        en=f"These jobs failed in the last pipeline of the default branch: {echoues}.",
        fr=f"Ces jobs ont échoué dans le dernier pipeline de la branche par défaut : {echoues}.",
    )


def test_la_forge_sait_ce_qui_tourne_et_ou(forge, projet_du_lab):
    """PREMIERE TRACE : les environnements, et les deploiements enregistres.

    Un job qui lance un script de deploiement deploie, mais GitLab n'en sait
    rien : sa page des environnements reste vide, et aucun historique ne dit
    quelle version tourne ou. Six mois plus tard, personne ne peut repondre a
    « qu'est-ce qui est en production ? » sans lire des journaux de jobs.

    Declarer l'environnement change cela cote serveur : la forge cree
    l'environnement et ENREGISTRE un deploiement a chaque passage. Le test
    mesure les deux, parce que l'environnement seul pourrait n'avoir jamais
    recu de deploiement reussi.
    """
    environnements = api(
        forge, f"/projects/{projet_du_lab['id']}/environments", "per_page=50"
    )
    assert isinstance(environnements, list) and environnements, message(
        en=(
            "The project holds no environment. The jobs do run a deployment "
            "script, but GitLab knows nothing about it: its environments page "
            "stays empty, and no history says which version runs where. Six "
            "months later nobody can answer 'what is in production?' without "
            "reading job logs."
        ),
        fr=(
            "Le projet ne porte aucun environnement. Les jobs lancent bien un "
            "script de déploiement, mais GitLab n'en sait rien : sa page des "
            "environnements reste vide, et aucun historique ne dit quelle "
            "version tourne où. Six mois plus tard, personne ne peut répondre "
            "à « qu'est-ce qui est en production ? » sans lire des journaux de "
            "jobs."
        ),
    )

    deploiements = api(
        forge, f"/projects/{projet_du_lab['id']}/deployments", "per_page=50"
    )
    assert isinstance(deploiements, list), message(
        en="The project's deployments could not be read.",
        fr="Les déploiements du projet n'ont pas pu être lus.",
    )
    reussis = [d for d in deploiements if d.get("status") == "success"]
    assert reussis, message(
        en=(
            f"The project holds {len(environnements)} environment(s) but no "
            "successful deployment. An environment that never received a "
            "deployment traces nothing: let a deployment job run through to "
            "the end."
        ),
        fr=(
            f"Le projet porte {len(environnements)} environnement(s) mais "
            "aucun déploiement réussi. Un environnement qui n'a jamais reçu de "
            "déploiement ne retrace rien : laissez un job de déploiement aller "
            "au bout."
        ),
    )


def test_l_image_deployee_existe_ailleurs_que_dans_le_runner(forge, projet_du_lab):
    """DEUXIEME TRACE : l'image, qui doit survivre au job qui l'a construite.

    Une image construite et jamais poussee meurt avec le conteneur du job. Le
    journal montre une construction reussie, et pourtant rien ne subsiste :
    aucun deploiement ne peut reposer sur cette image, et aucun retour arriere
    n'est possible.

    La seule preuve d'une publication est une etiquette dans le registre du
    projet. Le test ne demande ni nom d'image, ni forme d'etiquette.
    """
    depots = api(forge, f"/projects/{projet_du_lab['id']}/registry/repositories")
    assert isinstance(depots, list) and depots, message(
        en=(
            "The project's registry holds no repository. The build job's log "
            "shows a successful build, and nothing remains: the image died "
            "with the job's container. No deployment can rely on it, and no "
            "rollback is possible."
        ),
        fr=(
            "Le registre du projet ne porte aucun dépôt. Le journal du job de "
            "construction montre une construction réussie, et rien ne "
            "subsiste : l'image est morte avec le conteneur du job. Aucun "
            "déploiement ne peut reposer sur elle, et aucun retour arrière "
            "n'est possible."
        ),
    )

    etiquettes: list[str] = []
    for d in depots:
        if not isinstance(d, dict) or not d.get("id"):
            continue
        tags = api(
            forge,
            f"/projects/{projet_du_lab['id']}/registry/repositories/{d['id']}/tags",
            "per_page=50",
        )
        if isinstance(tags, list):
            etiquettes += [t.get("name") for t in tags if isinstance(t, dict) and t.get("name")]

    assert etiquettes, message(
        en=(
            "The registry holds a repository but no tag: nothing was pushed. "
            "Check the registry login and the push in the build job's log."
        ),
        fr=(
            "Le registre porte un dépôt mais aucune étiquette : rien n'a été "
            "poussé. Vérifiez la connexion au registre et le push dans le "
            "journal du job de construction."
        ),
    )


def test_la_production_attend_une_decision(configuration, pipeline_de_main):
    """QUATRIEME TRACE : qui a decide, et quand.

    Un deploiement de production qui part au moindre commit sur la branche par
    defaut ne laisse aucune trace de decision : la mise en production devient
    un effet de bord d'une fusion. Le jour ou il faut dire qui a decide de
    livrer, la reponse est « personne ».

    Deux reponses conviennent, et le test accepte les deux : le job attend une
    main humaine, ou bien il ne part que sur une etiquette, posee
    deliberement. Dans les deux cas, un commit ordinaire sur la branche par
    defaut ne doit pas le lancer.
    """
    production = {
        nom: corps
        for nom, corps in configuration.items()
        if "prod" in nom or "prod" in str(corps.get("environment") or "")
    }
    assert production, message(
        en=(
            "No production deployment job found in the compiled "
            "configuration. The level is about delivering: the chain has to "
            "reach production."
        ),
        fr=(
            "Aucun job de déploiement en production trouvé dans la "
            "configuration compilée. Le niveau porte sur la livraison : la "
            "chaîne doit atteindre la production."
        ),
    )

    par_nom = {j.get("name"): j.get("status") for j in pipeline_de_main["jobs"]}
    partis = {
        nom: par_nom[nom]
        for nom in production
        if nom in par_nom and par_nom[nom] not in ("manual", "skipped")
    }
    assert not partis, message(
        en=(
            f"These production jobs started on their own on the default "
            f"branch: {partis}. Going to production then becomes a side effect "
            "of a merge, and on the day someone asks who decided to ship, the "
            "answer is 'nobody'. Either the job waits for a human, or it only "
            "runs on a deliberately pushed tag."
        ),
        fr=(
            f"Ces jobs de production sont partis d'eux-mêmes sur la branche "
            f"par défaut : {partis}. La mise en production devient alors un "
            "effet de bord d'une fusion, et le jour où il faut dire qui a "
            "décidé de livrer, la réponse est « personne ». Soit le job attend "
            "une main humaine, soit il ne part que sur une étiquette posée "
            "délibérément."
        ),
    )
