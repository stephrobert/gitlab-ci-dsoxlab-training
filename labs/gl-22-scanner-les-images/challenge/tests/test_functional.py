"""Tests du lab gl-22-scanner-les-images.

CE LAB NOTE CE QUE LA FORGE A VU, JAMAIS CE QUI EST ECRIT. Un `.gitlab-ci.yml`
qui declare un job de scan ne prouve rien : le job peut ne jamais tourner,
tourner sur autre chose que l'image publiee, ou echouer sans rien laisser. Les
tests lisent donc l'API : les jobs d'un pipeline, leur statut, et les
ARTEFACTS qu'ils ont laisses, telecharges puis ouverts.

LA REGLE QUI A COUTE QUATRE REECRITURES ailleurs vaut ici : l'etat de depart
publie son image sans jamais la scanner, donc aucun job de scan, aucun
artefact, aucun echec du a une vulnerabilite, aucun `.trivyignore`. Chacun des
cinq tests porte sur une de ces absences, et aucun ne peut etre vert au depart.

CE QUE LES TESTS NE FONT PAS. Ils n'imposent ni le nom du job, ni sa place
exacte, ni la forme de la commande Trivy, ni le nom du fichier de rapport : ils
reconnaissent un rapport Trivy a son CONTENU (le champ `ArtifactName` du format
JSON de Trivy). Ils ne jugent pas non plus si la raison ecrite pour une
exception est VRAIE : ils mesurent qu'elle existe, qu'elle a du corps, et que
l'exception ne couvre que le finding trie. La verite d'une raison est
l'affaire d'une revue humaine, et c'est dit dans le scenario.

LE FINDING TRIE vient de la note posee par le setup dans
`/opt/dsoxlab/gl-22/NOTE-EQUIPE-SECURITE.txt` (ligne `FAUX-POSITIF: <id>`).
Le setup l'a releve sur le VRAI rapport de l'image : l'identifiant n'est donc
pas code en dur ici.

TROIS FAITS MESURES SUR CETTE INSTANCE QUE LES MESSAGES RESPECTENT :
  - un pipeline dont un job manuel attend porte le statut `manual`, pas
    `success` ;
  - un job range dans une etape que `stages:` ne declare pas fait refuser TOUTE
    la configuration : pipeline `failed`, ZERO job, `yaml_errors` a `null`. Le
    linter CI du projet est alors le seul a nommer la cause ;
  - le projet est designe par son chemin exact, jamais par une recherche : un
    projet supprime reste 30 jours en retention (`gitlab.projet`).
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    URL,
    fichier,
    forge_joignable,
    jobs,
    lint_configuration,
    pipelines,
    projet,
)

from conftest import lab_host, message  # noqa: E402

NOTE = "/opt/dsoxlab/gl-22/NOTE-EQUIPE-SECURITE.txt"

# Combien de pipelines de `main` on relit. L'etat de depart en porte un ou
# deux, un apprenant appliqué en ajoute quelques-uns : six couvrent tout le
# travail sans transformer le test en aspirateur d'artefacts.
PIPELINES_RELUS = 6

# Script execute SUR LA VM : il telecharge l'archive d'artefacts d'un job et en
# extrait, de chaque fichier JSON qui ressemble a un rapport Trivy, la liste
# (identifiant, severite, paquet) des vulnerabilites. Le rapport entier peut
# peser plusieurs Mo : on ne rapatrie que ce que les tests lisent. Le jeton est
# lu dans le fichier de la VM, il ne figure dans aucune ligne de commande.
EXTRAIRE = r"""
import io, json, sys, urllib.request, zipfile
sortie = {"rapports": [], "erreur": None}
try:
    jeton = open("/etc/dsoxlab/jeton-api").read().strip()
    req = urllib.request.Request(sys.argv[1], headers={"PRIVATE-TOKEN": jeton})
    with urllib.request.urlopen(req, timeout=60) as r:
        donnees = r.read()
    with zipfile.ZipFile(io.BytesIO(donnees)) as z:
        for nom in z.namelist():
            if not nom.lower().endswith(".json"):
                continue
            try:
                doc = json.loads(z.read(nom))
            except ValueError:
                continue
            if not isinstance(doc, dict) or "ArtifactName" not in doc:
                continue
            vulns = []
            for res in doc.get("Results") or []:
                for v in res.get("Vulnerabilities") or []:
                    vulns.append([v.get("VulnerabilityID"), v.get("Severity"), v.get("PkgName")])
            sortie["rapports"].append({
                "fichier": nom,
                "artefact": doc.get("ArtifactName"),
                "type": doc.get("ArtifactType"),
                "vulns": vulns,
            })
except Exception as e:
    sortie["erreur"] = str(e)
print(json.dumps(sortie))
"""


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
def finding_trie(forge):
    """L'identifiant que l'équipe sécurité a écarté, lu dans la note du setup.

    Une note absente est une panne du lab, pas un échec de l'apprenant : le
    message le dit, au lieu de laisser croire que l'exception est mal écrite.
    """
    r = forge.run(f"cat {NOTE}")
    trouve = re.search(r"^FAUX-POSITIF:\s*(\S+)", r.stdout, re.MULTILINE) if r.rc == 0 else None
    assert trouve, message(
        en=(
            f"The security team's note {NOTE} is missing or unreadable. The "
            "lab setup did not complete: replay it with dsoxlab run."
        ),
        fr=(
            f"La note de l'équipe sécurité {NOTE} est absente ou illisible. Le "
            "setup du lab n'est pas allé au bout : rejouez-le avec dsoxlab run."
        ),
    )
    return trouve.group(1)


def _rapports_du_job(host, projet_id: int, job_id: int) -> list[dict]:
    """Les rapports Trivy contenus dans l'archive d'artefacts d'un job."""
    url = f"{URL}/api/v4/projects/{projet_id}/jobs/{job_id}/artifacts"
    r = host.run(f"python3 -c {shlex.quote(EXTRAIRE)} {shlex.quote(url)}")
    if r.rc != 0 or not r.stdout.strip():
        return []
    try:
        return json.loads(r.stdout).get("rapports") or []
    except json.JSONDecodeError:
        return []


@pytest.fixture(scope="module")
def historique(forge, projet_du_lab):
    """Les derniers pipelines de `main`, du plus récent au plus ancien.

    Chaque pipeline porte ses jobs, et chaque job qui a laissé une archive
    d'artefacts porte les rapports Trivy qu'elle contient. Un job encore en
    cours n'est pas ouvert : son archive n'est pas finie.
    """
    resultat = []
    for p in pipelines(forge, ref="main", projet_id=projet_du_lab["id"])[:PIPELINES_RELUS]:
        liste = []
        for j in jobs(forge, p["id"], projet_du_lab["id"]):
            archive = j.get("artifacts_file") or any(
                a.get("file_type") == "archive" for a in (j.get("artifacts") or [])
            )
            termine = j.get("status") in ("success", "failed")
            rapports = _rapports_du_job(forge, projet_du_lab["id"], j["id"]) if archive and termine else []
            liste.append({**j, "rapports": rapports})
        resultat.append({"pipeline": p, "jobs": liste})
    return resultat


def _court(entree: dict) -> str:
    """Le SHA court du commit d'un pipeline, tel que le registre le nomme."""
    return str(entree["pipeline"]["sha"])[:8]


def _avec_rapport(entree: dict) -> list[dict]:
    return [j for j in entree["jobs"] if j["rapports"]]


def test_le_dernier_pipeline_a_scanne_et_garde_un_rapport(forge, projet_du_lab, historique):
    """LA MESURE DE BASE : un job a tourné, et un rapport existe dans la forge.

    Le pipeline de départ publie l'image et ne la scanne jamais : aucun job de
    scan, aucune archive d'artefacts contenant un rapport Trivy. Ce test ne
    peut donc pas être vert avant que l'apprenant ait écrit son job.

    Il lit le DERNIER pipeline de `main`, pas un ancien : un apprenant qui
    casse son scan au dernier commit ne doit pas être noté sur son avant-dernier.
    Le rapport se reconnaît à son contenu (format JSON de Trivy), pas à un nom
    de fichier ou de job.

    Le cas piège est le pipeline `failed` SANS AUCUN JOB : un job rangé dans
    une étape que `stages:` ne déclare pas fait refuser toute la configuration,
    et l'interface ne dit pas pourquoi. Le message appelle alors le linter.
    """
    assert historique, message(
        en="No pipeline on main: push your configuration.",
        fr="Aucun pipeline sur main : poussez votre configuration.",
    )
    dernier = historique[0]
    statut = dernier["pipeline"].get("status")
    assert statut not in ("created", "pending", "running", "waiting_for_resource"), message(
        en=(
            f"The latest pipeline is still {statut}. Wait for it to finish, "
            "then run the check again: an unfinished job has no report yet."
        ),
        fr=(
            f"Le dernier pipeline est encore {statut}. Attendez qu'il se "
            "termine, puis relancez la vérification : un job en cours n'a pas "
            "encore de rapport."
        ),
    )
    if not dernier["jobs"]:
        lint = lint_configuration(forge, projet_du_lab["id"], "main") or {}
        erreurs = lint.get("errors") or ["(le linter n'a rien dit)"]
        pytest.fail(
            message(
                en=(
                    f"The latest pipeline ({statut}) has no job at all: GitLab "
                    "refused the whole configuration. The pipeline page does not "
                    "say why. The CI linter of the project does:\n  "
                    + "\n  ".join(erreurs)
                    + "\nA job in a stage that `stages:` does not declare is the "
                    "usual cause."
                ),
                fr=(
                    f"Le dernier pipeline ({statut}) n'a aucun job : GitLab a "
                    "refusé toute la configuration, et la page du pipeline ne "
                    "dit pas pourquoi. Le linter CI du projet, lui, le dit :\n  "
                    + "\n  ".join(erreurs)
                    + "\nUn job rangé dans une étape que `stages:` ne déclare "
                    "pas en est la cause habituelle."
                ),
            )
        )
    assert _avec_rapport(dernier), message(
        en=(
            "No job of the latest pipeline left a Trivy JSON report in its "
            "artifacts. Either no job scans the image, or the job does not keep "
            "its report: it needs `artifacts: paths:` pointing at a file written "
            "with `--format json --output`, and `when: always` so that it is "
            "kept even when the job fails."
        ),
        fr=(
            "Aucun job du dernier pipeline n'a laissé de rapport JSON de Trivy "
            "dans ses artefacts. Soit aucun job ne scanne l'image, soit le job "
            "ne garde pas son rapport : il lui faut `artifacts: paths:` vers un "
            "fichier écrit avec `--format json --output`, et `when: always` pour "
            "qu'il soit conservé même quand le job échoue."
        ),
    )


def test_le_rapport_porte_sur_l_image_publiee_par_ce_pipeline(historique):
    """LE RAPPORT PORTE SUR LA BONNE IMAGE, pas sur n'importe laquelle.

    Un scan d'une image de démonstration, ou de `python:3.12`, produirait un
    beau rapport sans rapport avec ce que le pipeline livre. Le rapport de
    Trivy nomme ce qu'il a scanné (`ArtifactName`) : ce nom doit être l'image
    du registre de CE projet, au tag du commit de CE pipeline.

    C'est ce qui relie le scan à la publication, et c'est pourquoi le job de
    scan doit venir APRÈS la construction : avant, le tag n'existe pas encore
    et Trivy échoue à le tirer. Le test ne vérifie pas l'ordre des étapes, il
    vérifie son effet : un rapport du bon tag.
    """
    assert historique and _avec_rapport(historique[0]), message(
        en="The latest pipeline holds no Trivy report: see the previous test.",
        fr="Le dernier pipeline ne porte aucun rapport Trivy : voir le test précédent.",
    )
    entree = historique[0]
    court = _court(entree)
    noms = [r["artefact"] for j in _avec_rapport(entree) for r in j["rapports"]]
    bons = [
        n
        for n in noms
        if str(n).endswith(f":{court}") and "/root/pipeline-craft" in str(n)
    ]
    assert bons, message(
        en=(
            f"The report scans {noms}, not this pipeline's image. Expected a "
            f"name ending in /root/pipeline-craft:{court} (the registry image "
            "of this project, tagged with this commit's short SHA). In the job, "
            "that reference is $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA."
        ),
        fr=(
            f"Le rapport porte sur {noms}, pas sur l'image de ce pipeline. On "
            f"attend un nom qui finit par /root/pipeline-craft:{court} (l'image "
            "du registre de ce projet, taguée par le SHA court de ce commit). "
            "Dans le job, cette référence est "
            "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA."
        ),
    )


def test_une_critique_fait_echouer_le_pipeline_avant_tout_deploiement(historique):
    """LE BLOCAGE EST REEL : un pipeline portant une image vulnérable a échoué.

    L'état de départ publie une image qui porte une vulnérabilité critique, et
    déploie sans rien dire. Le lab veut qu'un seuil l'arrête. Ce test cherche,
    dans les derniers pipelines de `main`, un pipeline qui prouve les quatre
    faits du blocage :

      1. le job de scan a ÉCHOUÉ ;
      2. son rapport, conservé malgré l'échec, contient au moins une
         vulnérabilité CRITICAL : l'échec vient donc bien de la vulnérabilité,
         et non d'un registre injoignable ou d'un identifiant refusé ;
      3. le job n'est pas `allow_failure`, sinon son échec ne bloquerait rien ;
      4. aucun job de déploiement n'a réussi ni attendu une décision.

    Le pipeline entier doit alors être `failed`. Un pipeline sain de ce projet
    finit `manual` (le déploiement de production attend une main), jamais
    `success` : c'est donc `failed` qui prouve le blocage.

    POURQUOI UNE PREUVE PAR L'HISTORIQUE. Un apprenant qui corrige ensuite la
    base de l'image rend son dernier pipeline vert, et c'est la bonne fin. Le
    blocage reste lisible dans le pipeline qui l'a déclenché : sans lui, rien ne
    prouve que le seuil aurait arrêté la faille.
    """
    assert historique, message(
        en="No pipeline on main: push your configuration.",
        fr="Aucun pipeline sur main : poussez votre configuration.",
    )
    preuves = []
    bilan = []
    for entree in historique:
        pipeline = entree["pipeline"]
        for j in _avec_rapport(entree):
            if j.get("status") != "failed":
                continue
            critiques = [
                v for r in j["rapports"] for v in r["vulns"] if v[1] == "CRITICAL"
            ]
            deploiements = [
                x for x in entree["jobs"] if x.get("stage") == "deploy"
            ]
            ont_agi = [
                x["name"]
                for x in deploiements
                if x.get("status") in ("success", "running", "pending", "manual", "failed")
            ]
            bilan.append(
                f"pipeline {pipeline['id']} ({pipeline.get('status')}): "
                f"{len(critiques)} critique(s) dans le rapport, "
                f"allow_failure={j.get('allow_failure')}, "
                f"déploiements actifs={ont_agi}"
            )
            if (
                critiques
                and not j.get("allow_failure")
                and pipeline.get("status") == "failed"
                and not ont_agi
            ):
                preuves.append(pipeline["id"])
    assert preuves, message(
        en=(
            "No pipeline shows a real block. Expected: a scan job that failed, "
            "whose kept report lists at least one CRITICAL vulnerability, not "
            "`allow_failure`, with the whole pipeline failed and no deployment "
            "started. Seen: "
            + ("; ".join(bilan) if bilan else "no failed scan job with a report")
            + ". Check three things: the scan fails on severity "
            "(`--exit-code 1 --severity CRITICAL`), the report is kept when the "
            "job fails (`artifacts: when: always`), and the scan runs before "
            "the deploy stage."
        ),
        fr=(
            "Aucun pipeline ne montre un vrai blocage. On attend : un job de "
            "scan en échec, dont le rapport conservé liste au moins une "
            "vulnérabilité CRITICAL, qui n'est pas `allow_failure`, avec le "
            "pipeline entier en échec et aucun déploiement lancé. Constaté : "
            + ("; ".join(bilan) if bilan else "aucun job de scan en échec avec un rapport")
            + ". Trois points à vérifier : le scan échoue sur la sévérité "
            "(`--exit-code 1 --severity CRITICAL`), le rapport est conservé "
            "quand le job échoue (`artifacts: when: always`), et le scan passe "
            "avant l'étape de déploiement."
        ),
    )


def _lire_exceptions(contenu: str) -> list[tuple[str, int]]:
    """Les exceptions d'un `.trivyignore`, avec le nombre de mots de leur raison.

    La raison d'une exception est le texte des lignes de commentaire (`#`) qui
    la précèdent depuis l'exception d'avant. Les lignes vides ne coupent pas :
    un commentaire suivi d'une ligne blanche reste la raison de l'identifiant
    qui vient après.
    """
    exceptions = []
    mots = 0
    for ligne in contenu.splitlines():
        texte = ligne.strip()
        if not texte:
            continue
        if texte.startswith("#"):
            mots += len(texte.lstrip("#").split())
            continue
        identifiant = texte.split()[0]
        exceptions.append((identifiant, mots))
        mots = 0
    return exceptions


def test_l_exception_est_justifiee_et_ne_couvre_que_le_finding_trie(
    forge, projet_du_lab, finding_trie
):
    """ÉCARTER SANS JUSTIFIER est exactement ce qu'un attaquant espère.

    Une exception dans `.trivyignore` fait disparaître un finding du rapport
    et du seuil. Elle doit donc dire POURQUOI, à côté de l'identifiant, sinon
    personne ne sait six mois plus tard si c'était un faux positif ou une
    paresse. Le test lit le fichier tel que la forge le sert sur `main` et
    exige trois choses :

      1. l'exception du finding trié par l'équipe sécurité est présente ;
      2. elle est précédée d'une raison d'au moins quatre mots ;
      3. AUCUN AUTRE identifiant n'est écarté. Les autres critiques n'ont été
         triées par personne : les ignorer pour faire passer le pipeline est le
         contournement que ce lab apprend à reconnaître.

    Le test ne juge pas la VÉRITÉ de la raison, seulement son existence. C'est
    la limite d'un contrôle automatique, et le scénario la dit.
    """
    contenu = fichier(forge, ".trivyignore", "main", projet_du_lab["id"])
    assert contenu is not None, message(
        en=(
            "No .trivyignore at the root of main. The security team's "
            f"conclusion on {finding_trie} is not recorded anywhere, so the "
            "finding still blocks the pipeline."
        ),
        fr=(
            "Pas de .trivyignore à la racine de main. La conclusion de l'équipe "
            f"sécurité sur {finding_trie} n'est consignée nulle part : le "
            "finding bloque donc toujours le pipeline."
        ),
    )
    exceptions = _lire_exceptions(contenu)
    ids = [i for i, _ in exceptions]

    assert finding_trie in ids, message(
        en=(
            f"{finding_trie}, the finding the security team ruled out, is not "
            f"in .trivyignore (found: {ids or 'no entry'})."
        ),
        fr=(
            f"{finding_trie}, le finding que l'équipe sécurité a écarté, n'est "
            f"pas dans .trivyignore (trouvé : {ids or 'aucune entrée'})."
        ),
    )

    en_trop = sorted(set(ids) - {finding_trie})
    assert not en_trop, message(
        en=(
            f"These findings are ignored although nobody triaged them: "
            f"{en_trop}. An exception that lets the pipeline pass is not a fix: "
            "only the finding the security team ruled out may be ignored."
        ),
        fr=(
            f"Ces findings sont écartés alors que personne ne les a triés : "
            f"{en_trop}. Une exception qui fait passer le pipeline n'est pas une "
            "correction : seul le finding que l'équipe sécurité a écarté peut "
            "l'être."
        ),
    )

    mots = dict(exceptions)[finding_trie]
    assert mots >= 4, message(
        en=(
            f"The exception for {finding_trie} carries a reason of {mots} "
            "word(s). Write at least a sentence on the lines starting with # "
            "just above the identifier: why this finding does not concern this "
            "image."
        ),
        fr=(
            f"L'exception de {finding_trie} porte une raison de {mots} mot(s). "
            "Écrivez au moins une phrase sur les lignes qui commencent par # "
            "juste au-dessus de l'identifiant : pourquoi ce finding ne concerne "
            "pas cette image."
        ),
    )


def test_l_exception_est_effective_dans_le_dernier_rapport(historique, finding_trie):
    """ÉCRIRE L'EXCEPTION NE SUFFIT PAS : le dernier rapport ne doit plus la lister.

    Un `.trivyignore` mal placé, mal nommé ou non pris en compte par la commande
    laisse le finding dans le rapport, donc dans le seuil. La seule preuve que
    l'exception agit est dans le rapport du dernier pipeline : le finding trié
    n'y figure plus.

    Le test lit le rapport le plus récent, pas un ancien : un rapport d'avant
    l'exception listerait encore le finding, et ce serait justement le signe
    qu'il faut relancer le pipeline.

    Le test ne dit pas SEUL que l'exception est la cause : si l'apprenant a
    aussi corrigé la base de l'image, le finding disparaît pour une autre
    raison, et c'est acceptable. La rigueur de l'exception est mesurée par le
    test précédent.
    """
    for entree in historique:
        rapports = [r for j in _avec_rapport(entree) for r in j["rapports"]]
        if not rapports:
            continue
        ids = {v[0] for r in rapports for v in r["vulns"]}
        assert finding_trie not in ids, message(
            en=(
                f"The latest report (pipeline {entree['pipeline']['id']}) still "
                f"lists {finding_trie}. The exception is not taken into account: "
                "check the file name (.trivyignore, at the root of the repository, "
                "where the job runs) and run a new pipeline."
            ),
            fr=(
                f"Le dernier rapport (pipeline {entree['pipeline']['id']}) liste "
                f"encore {finding_trie}. L'exception n'est pas prise en compte : "
                "vérifiez le nom du fichier (.trivyignore, à la racine du dépôt, "
                "là où tourne le job) et lancez un nouveau pipeline."
            ),
        )
        return
    pytest.fail(
        message(
            en="No Trivy report in the recent pipelines of main: nothing to read.",
            fr="Aucun rapport Trivy dans les derniers pipelines de main : rien à lire.",
        )
    )
