"""Tests de l'epreuve gl-ep3-un-pipeline-qu-on-peut-auditer.

L'EPREUVE DE FIN DU NIVEAU c4. Le niveau s'appelle « Securiser », et une chaine
securisee n'est pas un outil : c'est une somme de petites garanties dont chacune
doit pouvoir etre lue par quelqu'un qui ne l'a pas construite. Un auditeur ne
croit pas sur parole, il interroge la forge.

CINQ PROMESSES NE SONT PAS TENUES, et aucun job n'echoue pour autant. C'est ce
qui rend l'enonce difficile : le pipeline est vert et le deploiement marche.

  1. LE SECRET DE DEPLOIEMENT n'est ni protege ni masque : il part vers
     n'importe quelle branche ou etiquette, et rien n'empeche un journal de le
     montrer ;
  2. MAIN SE REECRIT : tout Developer y pousse, historique reecrit compris ;
  3. UNE FUSION N'EXIGE PAS DE PIPELINE VERT ;
  4. LES IMAGES SONT DESIGNEES PAR UN TAG MOBILE, que son proprietaire peut
     deplacer sans prevenir ;
  5. AUCUN SCANNER n'a jamais tourne.

CE QUI EST NOTE RESTE UN ETAT, lu dans l'API : la variable, la branche
protegee, les reglages du projet, la configuration telle que GitLab l'a
compilee, et les jobs du dernier pipeline de `main`. Aucun test ne lit un
fichier du depot.

LES ROUTES PREMIUM NE SONT PAS DEMANDEES. `protected_environments` repond 404 en
CE, mesure en jouant gl-24. Chaque lecture ci-dessous porte sur une route qui
repond 200 en CE, sondee avant d'etre utilisee.
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

# Un job qui n'a pas fini, ou qui n'a pas reussi.
PAS_REUSSI = ("created", "pending", "running", "waiting_for_resource", "failed", "canceled")
# Les deux familles de rapports que les scanners du niveau deposent.
RAPPORTS_SCANNERS = ("sast", "secret_detection")
# Les jobs des templates de securite ne choisissent pas leurs images.
SCANNERS_PAR_NOM = ("sast", "secret_detection", "secret-detection", "semgrep")


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
def dernier_pipeline_main(forge, projet_du_lab):
    tous = pipelines(forge, ref="main", projet_id=projet_du_lab["id"])
    assert tous, message(
        en="No pipeline on the default branch: push your configuration.",
        fr="Aucun pipeline sur la branche par défaut : poussez votre configuration.",
    )
    dernier = tous[0]
    return {"pipeline": dernier, "jobs": jobs(forge, dernier["id"], projet_du_lab["id"])}


@pytest.fixture(scope="module")
def configuration(forge, projet_du_lab):
    """La configuration de `main` TELLE QUE GITLAB L'A COMPILEE."""
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
    return yaml.safe_load(rapport["merged_yaml"])


def _est_un_job(nom, corps) -> bool:
    reserves = {"stages", "workflow", "default", "variables", "include"}
    return isinstance(corps, dict) and nom not in reserves and not str(nom).startswith(".")


def _niveaux(liste) -> list:
    return [x.get("access_level") for x in (liste or []) if isinstance(x, dict)]


def test_le_secret_de_deploiement_est_tenu_comme_un_secret(forge, projet_du_lab):
    """PREMIERE PROMESSE : qui peut lire le secret de deploiement ?

    Une variable ni protegee ni masquee part vers TOUTE branche et TOUTE
    etiquette, y compris celles que n'importe quel Developer cree, et rien
    n'empeche un `echo` de la ranger dans un journal. L'auditeur lit le
    reglage dans l'API, pas dans le fichier du pipeline.

    La variable doit RESTER : la supprimer ferait tomber le deploiement, et le
    dernier test le mesure.
    """
    v = api(forge, f"/projects/{projet_du_lab['id']}/variables/DEPLOY_TOKEN")
    assert isinstance(v, dict) and v.get("key") == "DEPLOY_TOKEN", message(
        en=(
            "The deployment secret is no longer a variable of the project. The "
            "production job needs it: the secret must stay, with its settings "
            "fixed, rather than disappear."
        ),
        fr=(
            "Le secret de déploiement n'est plus une variable du projet. Le job "
            "de production en a besoin : le secret doit rester, avec ses "
            "réglages corrigés, plutôt que disparaître."
        ),
    )
    assert v.get("protected") is True, message(
        en=(
            "The deployment secret is handed to every branch and every tag, "
            "including those that any Developer creates. An auditor asking who "
            "can read it gets the answer 'everyone who can push'."
        ),
        fr=(
            "Le secret de déploiement est remis à toute branche et à toute "
            "étiquette, y compris celles que n'importe quel Développeur crée. "
            "Un auditeur qui demande qui peut le lire reçoit la réponse « tous "
            "ceux qui peuvent pousser »."
        ),
    )
    assert v.get("masked") is True, message(
        en=(
            "Nothing hides the deployment secret in job logs: one careless "
            "print and it is readable by everyone who can open the pipeline."
        ),
        fr=(
            "Rien ne cache le secret de déploiement dans les journaux de jobs : "
            "un affichage maladroit et il est lisible par tous ceux qui "
            "peuvent ouvrir le pipeline."
        ),
    )


def test_main_ne_se_reecrit_pas(forge, projet_du_lab):
    """DEUXIEME PROMESSE : qui peut changer ce qui part en production ?

    Une branche par defaut qui accepte les pushs de tout Developer et la
    reecriture d'historique n'a pas d'historique digne de ce nom : on ne peut
    plus dire, apres coup, ce qui a ete livre. La branche doit rester protegee
    (la supprimer de la liste la rendrait pire), avec un acces de push reserve
    aux Maintainers ou a personne, et sans push force.
    """
    b = api(forge, f"/projects/{projet_du_lab['id']}/protected_branches/main")
    assert isinstance(b, dict) and b.get("name") == "main", message(
        en=(
            "The default branch is not protected at all: anyone allowed to "
            "push can add, rewrite or delete the history that was shipped."
        ),
        fr=(
            "La branche par défaut n'est pas protégée du tout : quiconque peut "
            "pousser peut ajouter, réécrire ou supprimer l'historique qui a été "
            "livré."
        ),
    )
    push = _niveaux(b.get("push_access_levels"))
    assert push and all(n in (0, 40) for n in push), message(
        en=(
            f"The default branch accepts pushes from access levels {push}. A "
            "Developer can still change what goes to production without any "
            "review, and the audit trail ends where the push begins."
        ),
        fr=(
            f"La branche par défaut accepte les pushs des niveaux d'accès {push}. "
            "Un Développeur peut encore changer ce qui part en production sans "
            "relecture, et la piste d'audit s'arrête là où le push commence."
        ),
    )
    assert b.get("allow_force_push") is False, message(
        en=(
            "History of the default branch can still be rewritten by force "
            "push: what the auditor reads there proves nothing, since it can "
            "have been replaced afterwards."
        ),
        fr=(
            "L'historique de la branche par défaut peut encore être réécrit par "
            "push forcé : ce que l'auditeur y lit ne prouve rien, puisque "
            "cela a pu être remplacé après coup."
        ),
    )


def test_une_fusion_exige_un_pipeline_vert(forge, projet_du_lab):
    """TROISIEME PROMESSE : le pipeline qui juge doit avoir le dernier mot.

    Sans ce reglage, un pipeline rouge n'empeche pas la fusion : la verification
    existe, et personne n'est tenu de l'ecouter. Le reglage est un attribut du
    projet (route 200 en CE), pas une regle d'approbation Premium.
    """
    p = api(forge, f"/projects/{projet_du_lab['id']}")
    assert isinstance(p, dict), message(
        en="The project's settings could not be read.",
        fr="Les réglages du projet n'ont pas pu être lus.",
    )
    assert p.get("only_allow_merge_if_pipeline_succeeds") is True, message(
        en=(
            "A merge request can be merged while its pipeline is red. The "
            "checks run, but nothing obliges anyone to listen to them: the "
            "pipeline's verdict has no power."
        ),
        fr=(
            "Une demande de fusion peut être fusionnée alors que son pipeline "
            "est rouge. Les contrôles tournent, mais rien n'oblige à les "
            "écouter : le verdict du pipeline n'a aucun pouvoir."
        ),
    )


def test_ce_que_les_jobs_telechargent_est_epingle(configuration):
    """QUATRIEME PROMESSE : qu'est-ce qui tourne, exactement ?

    Un tag peut etre deplace par celui qui le possede : `alpine:3.24.2` designe
    aujourd'hui une image et peut en designer une autre demain, sans qu'aucune
    ligne du depot change. Seul le digest `@sha256:...` est immuable. Le test
    lit la configuration que GitLab a compilee, et il regarde les images des
    jobs du PROJET : les jobs des templates de scanners choisissent les leurs.
    """
    defaut = configuration.get("default") or {}
    images: dict[str, list[str]] = {}
    for nom, corps in configuration.items():
        if not _est_un_job(nom, corps):
            continue
        if any(marque in str(nom).lower() for marque in SCANNERS_PAR_NOM):
            continue
        liste = []
        img = corps.get("image", defaut.get("image", configuration.get("image")))
        if isinstance(img, dict):
            img = img.get("name")
        liste.append(img or "(aucune : celle du runner)")
        for s in corps.get("services") or []:
            liste.append(s.get("name") if isinstance(s, dict) else str(s))
        images[nom] = liste

    assert images, message(
        en="No job of the project was found in the compiled configuration.",
        fr="Aucun job du projet n'a été trouvé dans la configuration compilée.",
    )
    mobiles = {
        nom: [i for i in liste if "@sha256:" not in str(i)]
        for nom, liste in images.items()
    }
    mobiles = {nom: liste for nom, liste in mobiles.items() if liste}
    assert not mobiles, message(
        en=(
            f"These jobs rely on images that are not pinned: {mobiles}. The "
            "owner of a tag can move it at any time, so the same pipeline can "
            "run something different tomorrow with no trace in the history: "
            "nobody can say what ran."
        ),
        fr=(
            f"Ces jobs reposent sur des images non épinglées : {mobiles}. Le "
            "propriétaire d'un tag peut le déplacer à tout moment, et le même "
            "pipeline peut exécuter autre chose demain sans la moindre trace "
            "dans l'historique : personne ne peut dire ce qui a tourné."
        ),
    )


def test_le_dernier_pipeline_est_sain_et_porte_des_rapports(dernier_pipeline_main):
    """CINQUIEME PROMESSE, et le garde-fou des quatre autres.

    Deux choses se lisent ici. Les scanners ont tourne : au moins un job
    reussi depose un rapport `sast`, au moins un autre un rapport
    `secret_detection`. Et la chaine a tenu : aucun job ne reste en attente,
    n'echoue ou n'est annule, et la production s'est deployee. Corriger la
    securite en cassant le deploiement n'est pas un succes : proteger le secret
    d'une branche non protegee, par exemple, prive le job de production de son
    secret.
    """
    liste = dernier_pipeline_main["jobs"]
    par_nom = {j.get("name"): j.get("status") for j in liste}

    types_reussis: set[str] = set()
    for j in liste:
        if j.get("status") != "success":
            continue
        for a in j.get("artifacts") or []:
            if a.get("file_type") in RAPPORTS_SCANNERS:
                types_reussis.add(a["file_type"])
    manquants = [t for t in RAPPORTS_SCANNERS if t not in types_reussis]
    assert not manquants, message(
        en=(
            f"The latest pipeline of main holds no successful report of these "
            f"kinds: {manquants}. Nobody ever looked at the code or at what it "
            "contains: an auditor asking what was checked finds nothing to read."
        ),
        fr=(
            f"Le dernier pipeline de main ne porte aucun rapport réussi de ces "
            f"types : {manquants}. Personne n'a jamais regardé le code ni ce "
            "qu'il contient : un auditeur qui demande ce qui a été contrôlé "
            "n'a rien à lire."
        ),
    )

    abimes = {n: s for n, s in par_nom.items() if s in PAS_REUSSI}
    assert not abimes, message(
        en=(
            f"These jobs of the latest pipeline did not succeed: {abimes}. A "
            "chain that cannot finish is not a chain that can be audited."
        ),
        fr=(
            f"Ces jobs du dernier pipeline n'ont pas réussi : {abimes}. Une "
            "chaîne qui ne peut pas aller au bout n'est pas une chaîne qu'on "
            "peut auditer."
        ),
    )

    assert par_nom.get("deployer-production") == "success", message(
        en=(
            f"The production deployment job is {par_nom.get('deployer-production')!r} "
            "in the latest pipeline. Making the chain safer must not stop it "
            "from delivering."
        ),
        fr=(
            f"Le job de déploiement en production est "
            f"{par_nom.get('deployer-production')!r} dans le dernier pipeline. "
            "Rendre la chaîne plus sûre ne doit pas l'empêcher de livrer."
        ),
    )
