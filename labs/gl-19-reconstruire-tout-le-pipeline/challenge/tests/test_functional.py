"""Tests du lab gl-19-reconstruire-tout-le-pipeline.

L'EPREUVE DE SYNTHESE DU CATALOGUE. Le depot part sans un seul fichier de CI :
tous les tests de ce fichier sont faux au depart, non pas parce que le pipeline
est mal ecrit, mais parce qu'il n'existe pas.

CE QUI EST NOTE EST UN ETAT, PAS UNE IMPLEMENTATION. Chaque test reprend un
point du cahier des charges et le mesure sur ce que la forge montre : les
etapes d'un pipeline qui a tourne, les fichiers que GitLab a reellement
inclus, les instances d'une matrice, les cas de test remontes, le pipeline
enfant declenche, les etiquettes posees dans le registre, les verrous de
deploiement crees. Aucun test ne lit un fichier du depot, aucun n'impose un nom
de job, un nombre de fichiers inclus ou une version d'image.

POURQUOI UNE SYNTHESE NE SE NOTE PAS COMME UN LAB. Un lab mesure un geste ; une
epreuve mesure que les gestes TIENNENT ENSEMBLE. C'est pour cela qu'on retrouve
ici les mesures des labs 09, 10, 15, 16 et 18 : chacune a ete eprouvee seule,
et ce qui reste a prouver est qu'elles coexistent dans un seul pipeline vert.

UN POINT DU CAHIER DES CHARGES N'EST PAS MESURE ICI, et il faut le dire. « Gerer
les contextes de workflow : demande de fusion, branche par defaut, etiquettes »
demanderait d'ouvrir une demande de fusion et de poser une etiquette, donc deux
situations supplementaires a construire. Le lab 17 le mesure deja, sur le seul
cas ou il se trompe en silence. Ici, le `workflow:` est verifie par ce qu'il
produit : un pipeline qui nait sur la branche par defaut.
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
    lint_configuration,
    noms,
    pipelines,
    projet,
    stages,
)

from conftest import lab_host, message  # noqa: E402

# Les cinq etapes exigees par le cahier des charges. GitLab ajoute `.pre` et
# `.post` d'office : ils ne comptent pas.
ETAPES_EXIGEES = {"lint", "test", "orchestrate", "build", "deploy"}

# Les raisons d'echec qui viennent du CODE, et qu'une relance ne doit jamais
# rattraper. Meme regle qu'au lab 18, et pour la meme raison.
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
def pipeline(forge, projet_du_lab):
    """Le dernier pipeline de la branche par defaut, et ses jobs.

    Tout le reste en depend : sans pipeline, il n'y a rien a mesurer, et c'est
    exactement l'etat de depart de cette epreuve.
    """
    tous = pipelines(forge, ref="main")
    assert tous, message(
        en=(
            "No pipeline on the default branch. The repository starts without a "
            "single CI file: nothing runs until you write one and push it."
        ),
        fr=(
            "Aucun pipeline sur la branche par défaut. Le dépôt part sans un "
            "seul fichier de CI : rien ne tourne avant que vous en écriviez un "
            "et le poussiez."
        ),
    )
    dernier = tous[0]
    tous_jobs = jobs(forge, dernier["id"], projet_du_lab["id"])
    assert tous_jobs, message(
        en=(
            f"Pipeline {dernier['id']} holds no job. GitLab compiles the whole "
            "configuration before creating any job, and one defect anywhere "
            "stops all of them. Ask the project's CI linter why: "
            "/ci/lint?dry_run=true&ref=main."
        ),
        fr=(
            f"Le pipeline {dernier['id']} ne porte aucun job. GitLab compile "
            "toute la configuration avant de créer le moindre job, et un seul "
            "défaut quelque part les arrête tous. Demandez au linter CI du "
            "projet pourquoi : /ci/lint?dry_run=true&ref=main."
        ),
    )
    return {"pipeline": dernier, "jobs": tous_jobs}


def test_cinq_etapes_et_un_pipeline_qui_tient(pipeline):
    """LE PREMIER POINT DU CAHIER DES CHARGES : un pipeline multi-etapes qui passe.

    Les cinq etapes doivent exister ET porter des jobs : une etape declaree que
    rien ne remplit n'organise rien. Le garde-fou habituel ferme la marche,
    aucun job en echec, et il ne mesure rien a lui seul : il empeche de valider
    un pipeline rouge.
    """
    presentes = stages(pipeline["jobs"])
    manquantes = sorted(ETAPES_EXIGEES - presentes)
    assert not manquantes, message(
        en=(
            f"These stages carry no job: {manquantes}. Stages seen in the "
            f"pipeline: {sorted(presentes)}. The specification asks for lint, "
            "test, orchestrate, build and deploy, and a stage declared but "
            "left empty organises nothing."
        ),
        fr=(
            f"Ces étapes ne portent aucun job : {manquantes}. Étapes vues dans "
            f"le pipeline : {sorted(presentes)}. Le cahier des charges demande "
            "lint, test, orchestrate, build et deploy, et une étape déclarée "
            "que rien ne remplit n'organise rien."
        ),
    )

    echoues = [
        j.get("name") for j in pipeline["jobs"] if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=f"These jobs failed in the pipeline: {echoues}.",
        fr=f"Ces jobs ont échoué dans le pipeline : {echoues}.",
    )


def test_la_configuration_est_modulaire(forge, projet_du_lab):
    """DEUXIEME POINT : des templates locaux, et GitLab les a vraiment lus.

    On ne compte pas les fichiers du depot : on demande au linter ce qu'il a
    INCLUS. Un `include:` mal ecrit, pointant un chemin qui n'existe pas, fait
    refuser la configuration ; un fichier present mais jamais inclus ne change
    rien au pipeline. Seule la liste rendue par le linter prouve le montage.
    """
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

    inclus = rapport.get("includes") or []
    locaux = [
        i.get("location")
        for i in inclus
        if isinstance(i, dict) and i.get("type") in (None, "local")
    ]
    assert len(locaux) >= 2, message(
        en=(
            f"GitLab included {len(locaux)} local file(s): {locaux}. The "
            "specification asks for a modular CI: the jobs live in several "
            "files pulled in with `include: local`, not in one long file."
        ),
        fr=(
            f"GitLab a inclus {len(locaux)} fichier(s) local(aux) : {locaux}. "
            "Le cahier des charges demande une CI modulaire : les jobs vivent "
            "dans plusieurs fichiers tirés par `include: local`, pas dans un "
            "seul long fichier."
        ),
    )


def test_la_matrice_couvre_deux_versions_et_remonte_ses_resultats(forge, projet_du_lab, pipeline):
    """TROISIEME ET QUATRIEME POINTS : la matrice, et les resultats lisibles.

    UNE MATRICE SE RECONNAIT A SES INSTANCES. GitLab nomme chaque instance
    `job: [valeur, valeur]` : plusieurs jobs portent donc le meme prefixe avec
    des valeurs differentes entre crochets. Le test exige deux instances au
    moins, et deux versions de Python distinctes parmi elles.

    DES RESULTATS REMONTES NE SE DEVINENT PAS DANS UN JOURNAL. Le cahier des
    charges demande des rapports JUnit : GitLab les range alors dans le rapport
    de test du pipeline, que l'API sert sur `/pipelines/:id/test_report`. Un
    `pytest` qui ecrit son fichier sans le declarer en `reports: junit:` ne
    remplit pas ce rapport, et c'est precisement la difference entre un
    artefact et un resultat lisible.
    """
    instances = sorted(n for n in noms(pipeline["jobs"]) if "[" in n and "]" in n)
    assert len(instances) >= 2, message(
        en=(
            f"Found {len(instances)} matrix instance(s): {instances}. GitLab "
            "names them `job: [value, value]`. The specification asks for "
            "tests on Python 3.11 and 3.12."
        ),
        fr=(
            f"{len(instances)} instance(s) de matrice trouvée(s) : {instances}. "
            "GitLab les nomme `job: [valeur, valeur]`. Le cahier des charges "
            "demande des tests sur Python 3.11 et 3.12."
        ),
    )
    assert any("3.11" in n for n in instances) and any("3.12" in n for n in instances), message(
        en=(
            f"The matrix instances do not show both Python versions: "
            f"{instances}. The specification asks for 3.11 and 3.12."
        ),
        fr=(
            f"Les instances de la matrice ne montrent pas les deux versions de "
            f"Python : {instances}. Le cahier des charges demande 3.11 et 3.12."
        ),
    )

    rapport = api(
        forge,
        f"/projects/{projet_du_lab['id']}/pipelines/{pipeline['pipeline']['id']}/test_report",
    )
    assert isinstance(rapport, dict), message(
        en="The pipeline's test report could not be read.",
        fr="Le rapport de test du pipeline n'a pas pu être lu.",
    )
    total = rapport.get("total_count") or 0
    assert total > 0, message(
        en=(
            "The pipeline's test report is empty. A pytest run that writes its "
            "XML file without declaring it under `artifacts: reports: junit:` "
            "leaves a downloadable file and no readable result: GitLab shows "
            "nothing in the pipeline, and nothing in the merge request."
        ),
        fr=(
            "Le rapport de test du pipeline est vide. Un pytest qui écrit son "
            "fichier XML sans le déclarer sous `artifacts: reports: junit:` "
            "laisse un fichier téléchargeable et aucun résultat lisible : "
            "GitLab n'affiche rien dans le pipeline, et rien dans la demande "
            "de fusion."
        ),
    )
    echoues = rapport.get("failed_count") or 0
    assert echoues == 0, message(
        en=f"{echoues} test case(s) failed out of {total} in the test report.",
        fr=f"{echoues} cas de test en échec sur {total} dans le rapport de test.",
    )


def test_un_pipeline_enfant_genere_a_tourne(forge, projet_du_lab, pipeline):
    """CINQUIEME POINT : un enfant dynamique, et le parent porte son etat.

    Un job `trigger:` n'est pas un job ordinaire. GitLab le sert comme un PONT,
    sur `/pipelines/:id/bridges`, et le pipeline declenche vit dans
    `downstream_pipeline`. Le chercher parmi les jobs ne donne rien, ce qui est
    la premiere surprise de ce sujet.

    Le test exige que le pont existe, qu'il ait reellement declenche un enfant,
    et que l'etat de l'enfant ne soit pas en echec. Il n'impose pas la
    strategie : `mirror` fait porter au pont l'etat exact de l'enfant, `depend`
    le fait attendre mais compte comme reussi un enfant en echec dont un job
    est tolere. Les deux repondent au cahier des charges ; l'une est
    preferable, et le corrige dit pourquoi.
    """
    ponts = api(
        forge, f"/projects/{projet_du_lab['id']}/pipelines/{pipeline['pipeline']['id']}/bridges"
    )
    assert isinstance(ponts, list) and ponts, message(
        en=(
            "No trigger job in the pipeline. A job that starts a downstream "
            "pipeline carries a `trigger:` key, and GitLab serves it on "
            "/pipelines/:id/bridges, not among the ordinary jobs."
        ),
        fr=(
            "Aucun job de déclenchement dans le pipeline. Un job qui démarre un "
            "pipeline aval porte une clé `trigger:`, et GitLab le sert sur "
            "/pipelines/:id/bridges, pas parmi les jobs ordinaires."
        ),
    )

    enfants = [
        p.get("downstream_pipeline")
        for p in ponts
        if isinstance(p.get("downstream_pipeline"), dict)
    ]
    assert enfants, message(
        en=(
            f"The {len(ponts)} trigger job(s) started no downstream pipeline. "
            "The specification asks for a child pipeline generated as an "
            "artifact and triggered from it."
        ),
        fr=(
            f"Les {len(ponts)} job(s) de déclenchement n'ont démarré aucun "
            "pipeline aval. Le cahier des charges demande un pipeline enfant "
            "généré en artefact et déclenché depuis celui-ci."
        ),
    )

    mauvais = [
        f"{e.get('id')}:{e.get('status')}"
        for e in enfants
        if e.get("status") in ("failed", "canceled")
    ]
    assert not mauvais, message(
        en=f"These child pipelines did not finish well: {mauvais}.",
        fr=f"Ces pipelines enfants ne se sont pas bien terminés : {mauvais}.",
    )


def test_l_image_est_publiee_au_registre(forge, projet_du_lab):
    """SIXIEME POINT : une image construite et PUBLIEE.

    Une image construite et jamais poussee ne sort pas du runner : la seule
    preuve d'une publication est une etiquette dans le registre du projet. Le
    test ne demande ni nom d'image ni forme d'etiquette : il demande qu'il y en
    ait une.
    """
    depots = api(forge, f"/projects/{projet_du_lab['id']}/registry/repositories")
    assert isinstance(depots, list) and depots, message(
        en=(
            "The project's container registry holds no repository. An image "
            "built and never pushed never leaves the runner."
        ),
        fr=(
            "Le registre d'images du projet ne porte aucun dépôt. Une image "
            "construite et jamais poussée ne sort jamais du runner."
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
            "Check the login and the push in the build job's log."
        ),
        fr=(
            "Le registre porte un dépôt mais aucune étiquette : rien n'a été "
            "poussé. Vérifiez la connexion et le push dans le journal du job "
            "de construction."
        ),
    )


def test_les_deploiements_sont_serialises_bornes_et_relances_avec_mesure(
    forge, projet_du_lab, pipeline
):
    """SEPTIEME POINT : la fiabilite, mesuree comme au lab 18.

    Trois proprietes, deux sources. Les VERROUS se lisent cote serveur : GitLab
    cree un objet par verrou, et l'API les rend. Le DELAI et la RELANCE ne
    s'observent pas en un pipeline vert : ils se lisent dans la configuration
    compilee par GitLab, heritages du bloc `default:` resolus.

    La relance, enfin, ne doit JAMAIS rattraper un echec de script. C'est le
    seul reglage de ce cahier des charges qui peut rendre un pipeline moins
    fiable : un test instable rejoue finit par passer au hasard.
    """
    groupes = api(forge, f"/projects/{projet_du_lab['id']}/resource_groups")
    assert isinstance(groupes, list), message(
        en="The project's resource groups could not be read from the API.",
        fr="Les groupes de ressources du projet n'ont pas pu être lus dans l'API.",
    )
    assert groupes, message(
        en=(
            "The forge holds no deployment lock. Without one, two pipelines "
            "can deploy to the same environment at the same time, and the last "
            "one started is not necessarily the last one finished."
        ),
        fr=(
            "La forge ne porte aucun verrou de déploiement. Sans lui, deux "
            "pipelines peuvent déployer en même temps sur le même "
            "environnement, et le dernier parti n'est pas forcément le dernier "
            "arrivé."
        ),
    )

    rapport = lint_configuration(forge, projet_du_lab["id"], "main")
    assert rapport is not None and rapport.get("merged_yaml"), message(
        en="GitLab returned no merged configuration for branch main.",
        fr="GitLab n'a rendu aucune configuration compilée pour la branche main.",
    )
    import yaml

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
    configuration = {
        nom: corps
        for nom, corps in charge.items()
        if isinstance(corps, dict) and nom not in reserves and not nom.startswith(".")
    }
    deploiements = {
        nom: corps
        for nom, corps in configuration.items()
        if "deploy" in str(corps.get("stage") or "") or "deploy" in nom
    }
    assert deploiements, message(
        en="No deployment job found in the compiled configuration.",
        fr="Aucun job de déploiement trouvé dans la configuration compilée.",
    )

    sans_borne = sorted(nom for nom, corps in deploiements.items() if not corps.get("timeout"))
    assert not sans_borne, message(
        en=(
            f"These deployment jobs carry no `timeout`: {sans_borne}. They "
            "inherit the project's limit, one hour by default."
        ),
        fr=(
            f"Ces jobs de déploiement ne portent pas de `timeout` : "
            f"{sans_borne}. Ils héritent du délai du projet, une heure par "
            "défaut."
        ),
    )

    avec_relance = {
        nom: corps.get("retry") for nom, corps in configuration.items() if corps.get("retry")
    }
    assert avec_relance, message(
        en=(
            "No job carries a `retry`. The specification asks for a targeted "
            "retry: a runner that dies mid-job fails a pipeline that nothing "
            "was wrong with."
        ),
        fr=(
            "Aucun job ne porte de `retry`. Le cahier des charges demande une "
            "relance ciblée : un runner qui meurt en cours de job fait échouer "
            "un pipeline qui n'avait rien de faux."
        ),
    )

    aveugles = {}
    for nom, relance in avec_relance.items():
        if not isinstance(relance, dict):
            aveugles[nom] = "retry: <nombre>, sans `when:`"
            continue
        quand = relance.get("when")
        if quand is None:
            aveugles[nom] = "retry.max sans `when:`"
            continue
        valeurs = {quand} if isinstance(quand, str) else {str(v) for v in quand}
        if valeurs & RELANCES_INTERDITES:
            aveugles[nom] = f"when: {sorted(valeurs)}"

    assert not aveugles, message(
        en=(
            f"These retries also replay code failures: {aveugles}. A retry "
            "that covers `script_failure` (or `always`, or no `when:` at all) "
            "turns a flaky test into a test that eventually passes by chance."
        ),
        fr=(
            f"Ces relances rejouent aussi les échecs de code : {aveugles}. Une "
            "relance qui couvre `script_failure` (ou `always`, ou aucun "
            "`when:`) transforme un test instable en test qui finit par passer "
            "au hasard."
        ),
    )
