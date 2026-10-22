"""Tests de l'epreuve gl-ep1-un-pipeline-qui-dit-vrai.

L'EPREUVE DE FIN DU NIVEAU c1. Elle ne mesure pas quatre mots-cles : elle
mesure quatre PROMESSES que le pipeline de depart affiche sans les tenir.

  1. « les tests passent » : faux, le job de test a le droit d'echouer, donc le
     vert ne dit rien ;
  2. « les resultats sont la » : faux, le rapport est un fichier a telecharger
     et GitLab n'en lit pas une ligne ;
  3. « le jeton est protege » : faux, il est en clair dans un fichier versionne,
     donc dans l'historique et sous les yeux de tous ;
  4. « la production est maitrisee » : faux, elle se deploie depuis n'importe
     quelle branche, sans decision de personne.

AUCUN DEFAUT N'EST NOMME DANS L'ENONCE, et les messages d'echec de ces tests
sont ecrits en consequence : ils decrivent la promesse non tenue et sa
consequence, jamais la ligne a ecrire. Une epreuve qui donne la correction dans
son message d'erreur n'est plus une epreuve.

CE QUI EST NOTE RESTE UN ETAT. Le quatrieme test pousse une branche de travail
et regarde ce que la forge en fait : c'est la seule facon de savoir si la
production est protegee, et elle ne se lit pas dans un fichier.
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    api,
    api_ecrire,
    forge_joignable,
    jobs,
    lint_configuration,
    pipelines,
    projet,
)

from conftest import lab_host, message  # noqa: E402

# A quoi ressemble un secret laisse en clair. On ne cherche pas LA valeur de
# l'enonce : un apprenant qui remplacerait le jeton par un autre secret en dur
# n'aurait rien corrige.
FORMES_DE_SECRET = (
    re.compile(r"glpat-[A-Za-z0-9_-]{16,}"),
    re.compile(r"gl(?:dt|rt|cbt|soat)-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{30,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)

# La branche de travail que le quatrieme test pousse pour mesurer ce que la
# forge protege.
BRANCHE_ESSAI = "essai-de-l-epreuve"


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
def configuration(forge, projet_du_lab):
    """Les jobs de la configuration de `main` telle que GITLAB l'a compilee."""
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
        "brut": rapport["merged_yaml"],
        "racine": charge,
        "jobs": {
            nom: corps
            for nom, corps in charge.items()
            if isinstance(corps, dict) and nom not in reserves and not nom.startswith(".")
        },
    }


@pytest.fixture(scope="module")
def pipeline_de_main(forge, projet_du_lab):
    tous = pipelines(forge, ref="main")
    assert tous, message(
        en="No pipeline on the default branch: push your configuration.",
        fr="Aucun pipeline sur la branche par défaut : poussez votre configuration.",
    )
    dernier = tous[0]
    return {"pipeline": dernier, "jobs": jobs(forge, dernier["id"], projet_du_lab["id"])}


def _tests(configuration: dict) -> dict:
    """Les jobs qui testent, reconnus a leur etape ou a leur nom."""
    trouves = {}
    for nom, corps in configuration["jobs"].items():
        etape = str(corps.get("stage") or "")
        if "test" in etape or "test" in nom or "pytest" in nom:
            trouves[nom] = corps
    return trouves


def test_le_vert_du_pipeline_engage_les_tests(configuration, pipeline_de_main):
    """PREMIERE PROMESSE : un pipeline vert signifie que les tests passent.

    Un job autorise a echouer ne fait pas echouer son pipeline. Le vert cesse
    alors de porter l'information pour laquelle on le regarde, et personne ne
    s'en apercoit : la page du pipeline affiche le meme vert qu'avant.

    Le test exige donc deux choses : que plus aucun job de test ne soit
    autorise a echouer, et qu'ils aient REELLEMENT reussi. La seconde sans la
    premiere laisserait passer un pipeline vert par tolerance.
    """
    tests = _tests(configuration)
    assert tests, message(
        en="No test job found in the compiled configuration.",
        fr="Aucun job de test trouvé dans la configuration compilée.",
    )

    toleres = sorted(nom for nom, corps in tests.items() if corps.get("allow_failure"))
    assert not toleres, message(
        en=(
            f"These test jobs cannot fail the pipeline: {toleres}. The pipeline "
            "will stay green whatever the tests say, so its green no longer "
            "carries the one piece of information it is looked at for. Nobody "
            "notices, because the page shows the same green as before."
        ),
        fr=(
            f"Ces jobs de test ne peuvent pas faire échouer le pipeline : "
            f"{toleres}. Le pipeline restera vert quoi que disent les tests : "
            "son vert ne porte donc plus la seule information pour laquelle on "
            "le regarde. Et personne ne s'en aperçoit, puisque la page affiche "
            "le même vert qu'avant."
        ),
    )

    par_nom = {j.get("name"): j.get("status") for j in pipeline_de_main["jobs"]}
    mauvais = {n: s for n, s in par_nom.items() if n in tests and s != "success"}
    assert not mauvais, message(
        en=(
            f"The test jobs did not succeed in the last pipeline of the "
            f"default branch: {mauvais}."
        ),
        fr=(
            f"Les jobs de test n'ont pas réussi dans le dernier pipeline de la "
            f"branche par défaut : {mauvais}."
        ),
    )


def test_les_resultats_de_test_sont_lisibles_dans_gitlab(
    forge, projet_du_lab, pipeline_de_main
):
    """DEUXIEME PROMESSE : les resultats des tests sont consultables.

    Un fichier de rapport attache comme simple artefact est telechargeable, et
    rien de plus : GitLab ne l'ouvre pas, ne compte pas ses cas, et n'affiche
    rien dans la demande de fusion. Celui qui relit le code doit donc
    telecharger un XML pour savoir ce qui a ete teste, ce que personne ne fait.

    La mesure est le rapport de test du pipeline, cote serveur : il reste vide
    tant que le fichier n'est pas declare comme un rapport.
    """
    rapport = api(
        forge,
        f"/projects/{projet_du_lab['id']}/pipelines/{pipeline_de_main['pipeline']['id']}/test_report",
    )
    assert isinstance(rapport, dict), message(
        en="The pipeline's test report could not be read.",
        fr="Le rapport de test du pipeline n'a pas pu être lu.",
    )
    total = rapport.get("total_count") or 0
    assert total > 0, message(
        en=(
            "GitLab shows no test result for this pipeline. The report file is "
            "produced and attached, but the server never opens it: no test "
            "count on the pipeline, nothing in the merge request. Whoever "
            "reviews the code would have to download an XML file to find out "
            "what was tested, and nobody does that."
        ),
        fr=(
            "GitLab n'affiche aucun résultat de test pour ce pipeline. Le "
            "fichier de rapport est bien produit et attaché, mais le serveur "
            "ne l'ouvre jamais : aucun compte de tests sur le pipeline, rien "
            "dans la demande de fusion. Celui qui relit le code devrait "
            "télécharger un XML pour savoir ce qui a été testé, et personne ne "
            "le fait."
        ),
    )
    echoues = rapport.get("failed_count") or 0
    assert echoues == 0, message(
        en=f"{echoues} test case(s) failed out of {total}.",
        fr=f"{echoues} cas de test en échec sur {total}.",
    )


def test_aucun_secret_ne_vit_dans_le_depot(forge, projet_du_lab, configuration):
    """TROISIEME PROMESSE : le jeton de deploiement est protege.

    Un secret ecrit dans un fichier versionne est lisible par tout le monde,
    present dans l'historique meme apres suppression, et visible dans chaque
    journal de job qui l'affiche. Le revoquer demande de modifier le depot, ce
    qui retarde toujours la revocation.

    Le test mesure les deux moities du geste : plus aucune forme de secret dans
    la configuration compilee, et une variable existante cote PROJET, masquee,
    pour que la valeur ne reapparaisse pas dans les journaux.
    """
    trouves = []
    for forme in FORMES_DE_SECRET:
        trouves += forme.findall(configuration["brut"])
    assert not trouves, message(
        en=(
            f"{len(trouves)} secret(s) still live in the configuration, for "
            f"instance '{trouves[0][:12]}…'. A secret in a versioned file is "
            "readable by everyone, stays in the history even after being "
            "deleted, and revoking it means changing the repository, which "
            "always delays the revocation."
        ),
        fr=(
            f"{len(trouves)} secret(s) vivent encore dans la configuration, "
            f"par exemple « {trouves[0][:12]}… ». Un secret dans un fichier "
            "versionné est lisible par tout le monde, reste dans l'historique "
            "même après suppression, et le révoquer demande de modifier le "
            "dépôt, ce qui retarde toujours la révocation."
        ),
    )

    variables = api(forge, f"/projects/{projet_du_lab['id']}/variables", "per_page=100")
    assert isinstance(variables, list) and variables, message(
        en=(
            "The secret is gone from the file, and nothing replaced it: the "
            "project holds no CI variable. A job that needs a token still "
            "needs it to come from somewhere the repository does not carry."
        ),
        fr=(
            "Le secret a quitté le fichier, et rien ne l'a remplacé : le "
            "projet ne porte aucune variable de CI. Un job qui a besoin d'un "
            "jeton a toujours besoin qu'il vienne d'un endroit que le dépôt ne "
            "porte pas."
        ),
    )

    masquees = [v.get("key") for v in variables if v.get("masked")]
    assert masquees, message(
        en=(
            f"The project's variables are not masked: "
            f"{[v.get('key') for v in variables]}. An unmasked variable is "
            "printed in full in any job log that echoes it, so the secret "
            "leaks again, this time into logs that are often kept longer than "
            "the repository."
        ),
        fr=(
            f"Les variables du projet ne sont pas masquées : "
            f"{[v.get('key') for v in variables]}. Une variable non masquée "
            "s'affiche en entier dans tout journal de job qui l'écho : le "
            "secret fuit donc à nouveau, cette fois dans des journaux souvent "
            "conservés plus longtemps que le dépôt."
        ),
    )


def test_la_production_ne_part_pas_depuis_une_branche_de_travail(
    forge, projet_du_lab, configuration
):
    """QUATRIEME PROMESSE : la production est maitrisee.

    Un job de deploiement sans regle part sur toute branche. N'importe quelle
    branche d'essai pousse donc en production, sans que personne ait decide.

    CE TEST CREE UNE BRANCHE ET REGARDE CE QUE LA FORGE EN FAIT, parce que
    cette propriete ne se lit pas dans un fichier : les regles se combinent, le
    bloc `workflow:` peut en annuler une, et seule l'evaluation du serveur
    tranche.

    LA BRANCHE EST CREEE PAR L'API, ET C'EST UNE CORRECTION. Une premiere
    version passait par la copie de travail de la VM, et l'epreuve est sortie
    ROUGE sans que le corrige ait tort : `/opt/dsoxlab` est cree par un
    playbook en `become: true`, donc possede par root, alors que les tests
    tournent en ssh sous un compte ordinaire. Le `git commit` y echouait sur
    les droits. L'API ne touche pas au disque, et c'est de toute facon la
    convention de ce catalogue.
    """
    deploiements = {
        nom: corps
        for nom, corps in configuration["jobs"].items()
        if "deploy" in str(corps.get("stage") or "") or "deploy" in nom
    }
    assert deploiements, message(
        en="No deployment job found in the compiled configuration.",
        fr="Aucun job de déploiement trouvé dans la configuration compilée.",
    )

    projet_id = projet_du_lab["id"]
    # Une branche laissee par une passe precedente ferait mesurer un vieux
    # pipeline : elle part d'abord.
    api_ecrire(
        forge, "DELETE", f"/projects/{projet_id}/repository/branches/{BRANCHE_ESSAI}"
    )
    code, corps = api_ecrire(
        forge,
        "POST",
        f"/projects/{projet_id}/repository/branches",
        {"branch": BRANCHE_ESSAI, "ref": "main"},
    )
    assert code in (200, 201), message(
        en=(
            f"The check branch could not be created through the API (HTTP "
            f"{code}): {str(corps)[:200]}. This test needs it to measure what "
            "the forge protects."
        ),
        fr=(
            f"La branche de contrôle n'a pas pu être créée par l'API (HTTP "
            f"{code}) : {str(corps)[:200]}. Ce test en a besoin pour mesurer "
            "ce que la forge protège."
        ),
    )

    # UN COMMIT, et pas seulement une branche : c'est le push d'un changement
    # qui doit etre juge, et une branche creee sans commit ne declenche pas
    # forcement le meme pipeline.
    #
    # L'ENDPOINT D'UN SEUL FICHIER, ET NON CELUI DES COMMITS, et c'est une
    # mesure du 2026-10-22 : `/repository/commits` attend un TABLEAU
    # d'actions, qu'un corps de formulaire ne sait pas porter. GitLab repond
    # « 400 Bad request - actions must be an array ». `/repository/files/:chemin`
    # cree un commit d'un seul fichier et se contente de champs simples.
    code, corps = api_ecrire(
        forge,
        "POST",
        f"/projects/{projet_id}/repository/files/CONTROLE-EPREUVE.md",
        {
            "branch": BRANCHE_ESSAI,
            "commit_message": "docs: une ligne pour declencher un pipeline",
            "content": "Fichier pose par le controle de l epreuve.\n",
        },
    )
    assert code in (200, 201), message(
        en=(
            f"The check commit could not be created through the API (HTTP "
            f"{code}): {str(corps)[:200]}."
        ),
        fr=(
            f"Le commit de contrôle n'a pas pu être créé par l'API (HTTP "
            f"{code}) : {str(corps)[:200]}."
        ),
    )

    try:
        # Le pipeline de cette branche, s'il y en a un : une configuration qui
        # refuse les branches de travail est une reponse valable.
        attendus = None
        for _ in range(40):
            tous = pipelines(forge, ref=BRANCHE_ESSAI)
            if not tous:
                time.sleep(5)
                continue
            attendus = tous[0]
            if attendus.get("status") not in ("created", "pending", "running"):
                break
            time.sleep(10)

        if attendus is None:
            # Aucun pipeline sur la branche de travail : la production ne peut
            # pas y partir. La promesse est tenue.
            return

        noms_deployeurs = sorted(
            j.get("name")
            for j in jobs(forge, attendus["id"], projet_du_lab["id"])
            if j.get("name") in deploiements
        )
        assert not noms_deployeurs, message(
            en=(
                f"Pushing the branch '{BRANCHE_ESSAI}' created these "
                f"deployment jobs: {noms_deployeurs}. Any trial branch "
                "therefore reaches the deployed environments, and nobody "
                "decided it: the job runs because the push happened."
            ),
            fr=(
                f"Le push de la branche « {BRANCHE_ESSAI} » a créé ces jobs de "
                f"déploiement : {noms_deployeurs}. N'importe quelle branche "
                "d'essai atteint donc les environnements déployés, et personne "
                "ne l'a décidé : le job part parce que le push a eu lieu."
            ),
        )
    finally:
        # La branche de controle ne reste pas : elle n'appartient pas a
        # l'epreuve, et la laisser ferait demarrer la prochaine passe dans un
        # etat different.
        api_ecrire(
            forge, "DELETE", f"/projects/{projet_id}/repository/branches/{BRANCHE_ESSAI}"
        )
