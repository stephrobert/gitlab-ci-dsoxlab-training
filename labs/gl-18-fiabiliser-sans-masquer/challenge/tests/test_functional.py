"""Tests du lab gl-18-fiabiliser-sans-masquer.

CE LAB NOTE DEUX CHOSES DE NATURE DIFFERENTE, et la distinction est le coeur du
sujet.

LA PREMIERE EST UN EFFET SERVEUR. Un `resource_group` n'est pas une ligne de
YAML : GitLab cree un VERROU NOMME, que l'API rend sur
`/projects/:id/resource_groups`. Mesure le 2026-10-22 sur l'instance du lab :
l'endpoint repond 200 et rend `[]` avant tout travail. Les verrous se comptent
donc comme on compte des pipelines, sur l'etat laisse dans la forge.

LA SECONDE NE S'OBSERVE PAS EN UN SEUL PIPELINE, et c'est pourquoi elle se lit
autrement. Un `retry` ne se voit que le jour ou le runner tombe ; un `timeout`
de vingt minutes, que le jour ou un job depasse vingt minutes ; un
`interruptible: false`, que le jour ou un second push arrive pendant un
deploiement. Provoquer ces trois pannes prendrait plus longtemps que le lab
entier. Les tests lisent donc la configuration COMPILEE PAR GITLAB, le
`merged_yaml` du linter : ce n'est pas le fichier du depot relu cote poste,
c'est ce que le serveur a compris, heritages du bloc `default:` resolus.

CE QUE LES TESTS NE FONT PAS. Ils ne cherchent ni un nom de verrou, ni une
valeur de `timeout`, ni une liste de raisons de relance precise. Un apprenant
qui nomme ses verrous autrement, ou qui choisit d'autres raisons
d'infrastructure, a reussi. Ce qui est note, c'est la propriete : les
deploiements sont serialises, les jobs longs ont une borne, les deploiements ne
s'annulent pas, et la relance NE RATTRAPE PAS un echec de script.

CE DERNIER POINT EST LE SUJET. Un `retry: 2` nu rejoue aussi un test qui
echoue, et un test instable finit par passer au hasard : la relance masque
alors exactement ce qu'on lui demande de signaler. C'est le seul endroit du
catalogue ou un reglage de fiabilite peut rendre un pipeline MOINS fiable.
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

# Les raisons d'echec qui viennent du CODE, et qu'une relance ne doit jamais
# rattraper : un script qui echoue a echoue.
RELANCES_INTERDITES = {"always", "script_failure"}


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
def rapport(forge, projet_du_lab):
    """Ce que GitLab dit de la configuration de `main`, compilation comprise."""
    r = lint_configuration(forge, projet_du_lab["id"], "main")
    assert r is not None, message(
        en=(
            "GitLab's CI linter did not answer for branch main. Nothing can be "
            "measured on a missing reading, so this test refuses to conclude."
        ),
        fr=(
            "Le linter CI de GitLab n'a pas répondu pour la branche main. Rien "
            "ne se conclut sur une mesure absente : ce test refuse de trancher."
        ),
    )
    return r


@pytest.fixture(scope="module")
def configuration(rapport):
    """Les jobs de la configuration COMPILEE, heritages resolus.

    On ne relit pas `.gitlab-ci.yml` : on lit ce que le serveur a compris. La
    difference compte dans ce lab, parce que `interruptible` est pose dans le
    bloc `default:` du fichier principal et doit etre surcharge job par job.
    """
    assert rapport.get("valid") is True, message(
        en=(
            "GitLab still refuses the configuration of main:\n  "
            + "\n  ".join(rapport.get("errors") or ["(no reason given)"])
            + "\nAs long as it is refused, the pipeline is born failed with "
            "zero job, and nothing can be made reliable."
        ),
        fr=(
            "GitLab refuse encore la configuration de main :\n  "
            + "\n  ".join(rapport.get("errors") or ["(aucune raison donnée)"])
            + "\nTant qu'elle est refusée, le pipeline naît en échec avec zéro "
            "job, et il n'y a rien à fiabiliser."
        ),
    )
    brut = rapport.get("merged_yaml")
    assert brut, message(
        en="The linter accepted the configuration but returned no merged YAML.",
        fr="Le linter accepte la configuration mais ne rend aucun YAML compilé.",
    )
    charge = yaml.safe_load(brut)
    assert isinstance(charge, dict), message(
        en="The merged YAML returned by GitLab could not be read.",
        fr="Le YAML compilé rendu par GitLab n'a pas pu être lu.",
    )
    # Les cles qui ne sont pas des jobs : mots-cles de haut niveau.
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


def _deploiements(configuration: dict) -> dict:
    """Les jobs qui deploient, reconnus a leur etape ou a leur nom.

    On ne code pas une liste de noms : un apprenant peut renommer ses jobs. Un
    job de deploiement est un job dont l'etape ou le nom parle de deploiement.
    """
    trouves = {}
    for nom, corps in configuration.items():
        etape = str(corps.get("stage") or "")
        if "deploy" in etape or "deploy" in nom or "déploi" in nom:
            trouves[nom] = corps
    return trouves


def test_les_deploiements_sont_serialises_par_un_verrou(forge, projet_du_lab, configuration):
    """LA MESURE SERVEUR : la forge a-t-elle cree les verrous ?

    Deux deploiements qui partent en meme temps sur le meme environnement se
    marchent dessus, et le dernier arrive n'est pas forcement le dernier
    termine. `resource_group` cree un verrou nomme : GitLab met le second job
    en attente au lieu de le lancer.

    Ce test ne lit pas le YAML pour cela. Il demande a la forge quels verrous
    elle porte, puis verifie que chaque verrou declare dans la configuration y
    figure. L'endpoint rend `[]` tant que rien n'a ete pose : le lab part donc
    bien de zero.
    """
    deploiements = _deploiements(configuration)
    assert deploiements, message(
        en=(
            "No deployment job found in the compiled configuration. The lab "
            "expects the deployment jobs of ci/deploy.yml to exist."
        ),
        fr=(
            "Aucun job de déploiement trouvé dans la configuration compilée. "
            "Le lab attend les jobs de déploiement de ci/deploy.yml."
        ),
    )

    declares = {
        str(corps["resource_group"])
        for corps in deploiements.values()
        if corps.get("resource_group")
    }
    sans_verrou = sorted(
        nom for nom, corps in deploiements.items() if not corps.get("resource_group")
    )
    assert not sans_verrou, message(
        en=(
            f"These deployment jobs carry no lock: {sans_verrou}. Without one, "
            "two pipelines can deploy to the same environment at the same "
            "time, and the last one started is not necessarily the last one "
            "finished."
        ),
        fr=(
            f"Ces jobs de déploiement ne portent aucun verrou : {sans_verrou}. "
            "Sans lui, deux pipelines peuvent déployer en même temps sur le "
            "même environnement, et le dernier parti n'est pas forcément le "
            "dernier arrivé."
        ),
    )

    groupes = api(forge, f"/projects/{projet_du_lab['id']}/resource_groups")
    assert isinstance(groupes, list), message(
        en="The project's resource groups could not be read from the API.",
        fr="Les groupes de ressources du projet n'ont pas pu être lus dans l'API.",
    )
    noms_forge = {str(g.get("key")) for g in groupes if isinstance(g, dict)}

    manquants = sorted(declares - noms_forge)
    assert not manquants, message(
        en=(
            f"The configuration declares the locks {sorted(declares)}, but the "
            f"forge only holds {sorted(noms_forge) or 'none'}. A lock is "
            "created when a pipeline that carries it is created: push the "
            "configuration and let a pipeline run on the default branch."
        ),
        fr=(
            f"La configuration déclare les verrous {sorted(declares)}, mais la "
            f"forge n'en porte que {sorted(noms_forge) or 'aucun'}. Un verrou "
            "se crée quand un pipeline qui le porte est créé : poussez la "
            "configuration et laissez un pipeline tourner sur la branche par "
            "défaut."
        ),
    )


def test_la_relance_ne_rattrape_pas_un_echec_de_script(configuration):
    """LE SUJET DU LAB : une relance qui masque un bug est une regression.

    Un job peut echouer pour deux familles de raisons tres differentes. Le
    runner tombe, l'API ne repond pas, le job reste en attente : rejouer a du
    sens, rien n'etait faux. Le script echoue : rejouer ne fait que reporter le
    diagnostic, et un test instable finit par passer au hasard.

    Le test exige donc qu'une relance existe quelque part, et qu'AUCUNE ne
    couvre `always` ni `script_failure`. Il n'impose pas la liste des raisons
    retenues : il y en a plus d'une bonne.
    """
    avec_relance = {
        nom: corps.get("retry") for nom, corps in configuration.items() if corps.get("retry")
    }
    assert avec_relance, message(
        en=(
            "No job carries a `retry`. A runner that dies mid-job fails a "
            "pipeline that nothing was wrong with: the jobs exposed to "
            "infrastructure failures deserve a bounded retry."
        ),
        fr=(
            "Aucun job ne porte de `retry`. Un runner qui meurt en cours de "
            "job fait échouer un pipeline qui n'avait rien de faux : les jobs "
            "exposés aux pannes d'infrastructure méritent une relance bornée."
        ),
    )

    aveugles = {}
    for nom, relance in avec_relance.items():
        # `retry: 2` est la forme courte, et elle vaut « rejoue n'importe quel
        # echec » : c'est precisement la forme que le lab refuse.
        if not isinstance(relance, dict):
            aveugles[nom] = "retry: <nombre>, sans `when:`"
            continue
        quand = relance.get("when")
        if quand is None:
            aveugles[nom] = "retry.max sans `when:`"
            continue
        valeurs = {quand} if isinstance(quand, str) else {str(v) for v in quand}
        interdites = valeurs & RELANCES_INTERDITES
        if interdites:
            aveugles[nom] = f"when: {sorted(valeurs)}"

    assert not aveugles, message(
        en=(
            f"These retries also replay code failures: {aveugles}. A retry "
            "that covers `script_failure` (or `always`, or no `when:` at all, "
            "which means the same) turns a flaky test into a test that "
            "eventually passes by chance. It hides exactly what it is meant "
            "to report. Restrict `when:` to infrastructure failure reasons."
        ),
        fr=(
            f"Ces relances rejouent aussi les échecs de code : {aveugles}. Une "
            "relance qui couvre `script_failure` (ou `always`, ou aucun "
            "`when:`, ce qui revient au même) transforme un test instable en "
            "test qui finit par passer au hasard. Elle masque exactement ce "
            "qu'elle devrait signaler. Restreignez `when:` aux raisons "
            "d'échec d'infrastructure."
        ),
    )


def test_les_jobs_longs_sont_bornes_et_les_deploiements_ininterruptibles(
    forge, projet_du_lab, configuration, rapport
):
    """Deux bornes que le pipeline de depart n'a pas, et un garde-fou.

    UN `timeout` PAR JOB, d'abord. Sans lui, un job herite du delai du projet,
    qui vaut une heure par defaut : un job bloque occupe un runner pendant une
    heure avant que quiconque l'apprenne.

    UN DEPLOIEMENT NON INTERRUPTIBLE, ensuite, et c'est l'inverse du reglage
    qui convient a un build. Le fichier principal pose `interruptible: true`
    dans son bloc `default:`, ce qui est bon pour un build (annule, il ne
    laisse rien derriere lui) et dangereux pour un deploiement : interrompu au
    milieu, il laisse l'environnement dans un etat que personne n'a decrit.
    C'est pour cela que le test lit la configuration COMPILEE, ou l'heritage du
    bloc `default:` est deja resolu.

    Le garde-fou habituel ferme la marche : aucun job en echec dans le dernier
    pipeline de la branche par defaut. Il ne mesure rien a lui seul, il
    empeche de valider un pipeline rouge.
    """
    deploiements = _deploiements(configuration)
    assert deploiements, message(
        en="No deployment job found in the compiled configuration.",
        fr="Aucun job de déploiement trouvé dans la configuration compilée.",
    )

    sans_borne = sorted(nom for nom, corps in deploiements.items() if not corps.get("timeout"))
    assert not sans_borne, message(
        en=(
            f"These deployment jobs carry no `timeout`: {sans_borne}. They "
            "inherit the project's limit, one hour by default: a stuck "
            "deployment holds a runner for an hour before anyone hears about "
            "it."
        ),
        fr=(
            f"Ces jobs de déploiement ne portent pas de `timeout` : "
            f"{sans_borne}. Ils héritent du délai du projet, une heure par "
            "défaut : un déploiement bloqué occupe un runner pendant une heure "
            "avant que quiconque l'apprenne."
        ),
    )

    annulables = sorted(
        nom for nom, corps in deploiements.items() if corps.get("interruptible") is not False
    )
    assert not annulables, message(
        en=(
            f"These deployment jobs can still be cancelled by the next push: "
            f"{annulables}. The main file sets `interruptible: true` in its "
            "`default:` block, which suits a build and endangers a "
            "deployment: interrupted halfway, it leaves the environment in a "
            "state nobody described. Override it per job."
        ),
        fr=(
            f"Ces jobs de déploiement restent annulables par le push suivant : "
            f"{annulables}. Le fichier principal pose `interruptible: true` "
            "dans son bloc `default:`, ce qui convient à un build et met un "
            "déploiement en danger : interrompu au milieu, il laisse "
            "l'environnement dans un état que personne n'a décrit. Surchargez "
            "le réglage job par job."
        ),
    )

    # Ce que la forge dit des valeurs choisies, pour information. GitLab 19.5.1
    # declare perimees deux anciennes raisons de relance, `stuck_or_timeout_failure`
    # et `job_execution_timeout`, eclatees en raisons plus precises. Le lab ne
    # fait pas echouer celui qui les utilise encore, parce qu'elles restent
    # acceptees ; il le dit, et le corrige montre la forme a jour.
    perimees = [
        a
        for a in (rapport.get("warnings") or [])
        if "deprecated" in a.lower() and "retry" in a.lower()
    ]
    if perimees:
        print("\nLa forge accepte, mais signale des valeurs périmées :")
        for a in perimees:
            print(f"  {a}")

    dernier = pipelines(forge, ref="main")
    assert dernier, message(
        en="No pipeline on the default branch: push your configuration.",
        fr="Aucun pipeline sur la branche par défaut : poussez votre configuration.",
    )
    echoues = [
        j.get("name")
        for j in jobs(forge, dernier[0]["id"], projet_du_lab["id"])
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=f"These jobs failed in the last pipeline of the default branch: {echoues}.",
        fr=f"Ces jobs ont échoué dans le dernier pipeline de la branche par défaut : {echoues}.",
    )
