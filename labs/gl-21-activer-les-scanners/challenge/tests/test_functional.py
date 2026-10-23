"""Tests du lab gl-21-activer-les-scanners.

CE LAB NOTE LES RAPPORTS, PAS LA CONFIGURATION. Un `.gitlab-ci.yml` qui
declare `include: template: Jobs/SAST.gitlab-ci.yml` ne prouve rien : le
template peut etre mal place, l'etape manquer, l'image du scanner ne pas se
telecharger. Ce qui compte est qu'un JOB AIT TOURNE et qu'un ARTEFACT EXISTE.
Les tests lisent donc, dans l'API, les jobs des pipelines de `main` et les
rapports JSON qu'ils ont deposes.

POURQUOI DES ARTEFACTS ET PAS UN TABLEAU DE BORD. L'instance du catalogue est
une GitLab CE. Le Security Dashboard, le rapport de vulnerabilites du projet et
les merge request approval policies n'y existent pas (ils sont Ultimate), et le
lab n'en fait rien pratiquer. SAST et Secret Detection, eux, tournent en CE et
rendent leur resultat dans un fichier JSON (`gl-sast-report.json`,
`gl-secret-detection-report.json`). Le lecteur lit ce fichier.

COMMENT UN RAPPORT SE RECONNAIT. Pas a son nom de job : un apprenant peut
renommer ou etendre le job du template. Le job de l'API porte la liste de ses
artefacts, et chacun a un `file_type`. Un rapport SAST est un artefact de type
`sast`, un rapport de Secret Detection un artefact de type `secret_detection`.

L'ETAT DE DEPART NE PORTE AUCUN DE CES RAPPORTS. Le setup livre un pipeline
sain (un job de test) et un jeton GitLab ecrit en dur dans `app/config.py`.
Chaque test ci-dessous exige quelque chose que ce pipeline ne produit pas :
un rapport, la trace qu'un scan a VU le defaut, la correction constatee par un
nouveau scan, ou la lecture consignee. Aucun ne peut donc etre vert avant le
travail.

CE QUE LES TESTS NE FONT PAS. Ils ne nomment ni le job, ni l'analyseur, ni le
fichier de configuration, et ils n'imposent pas de variable de projet pour
ranger le secret. Ils ne comptent pas non plus les vulnerabilites du rapport
SAST : sur une petite application, il peut etre vide, et un rapport vide est
un resultat, pas une panne.
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
    api,
    fichier,
    forge_joignable,
    jobs,
    pipelines,
    projet,
)

from conftest import lab_host, message  # noqa: E402

# Le fichier ou le setup a plante le defaut, et la forme du jeton plante. Le
# motif est assemble en deux morceaux : le catalogue ne doit contenir aucune
# forme complete de jeton GitLab, un detecteur de secrets y verrait un vrai.
FICHIER_DEFAUT = "app/config.py"
MOTIF_JETON = re.compile("glpat" + r"-[0-9A-Za-z_-]{20}")
# Ce par quoi un rapport de Secret Detection designe cette regle, quand l'extrait
# de code est masque ou absent : l'identifiant de regle ou son libelle.
SIGNATURES_JETON = ("glpat", "gitlab_personal_access_token", "gitlab personal access token")

TYPE_SAST = "sast"
TYPE_SECRETS = "secret_detection"
NOM_SAST = "gl-sast-report.json"
NOM_SECRETS = "gl-secret-detection-report.json"

# Les statuts d'un job qui n'a PAS produit de resultat exploitable.
ECHECS = ("failed", "canceled")


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
def pipelines_main(forge, projet_du_lab):
    """Les pipelines de `main`, du plus recent au plus ancien (vingt au plus)."""
    return pipelines(forge, ref="main", projet_id=projet_du_lab["id"])


def _jobs_avec_rapport(forge, projet_id: int, pipeline: dict, type_rapport: str) -> list:
    """Les jobs REUSSIS d'un pipeline qui ont depose un artefact de ce type.

    Un job en echec n'est pas retenu, meme s'il a laisse un fichier : un scan
    interrompu en cours de route rend un rapport partiel, et lire un rapport
    partiel comme un resultat serait pire que ne rien lire.
    """
    retenus = []
    for job in jobs(forge, pipeline["id"], projet_id):
        if job.get("status") != "success":
            continue
        types = {a.get("file_type") for a in (job.get("artifacts") or []) if isinstance(a, dict)}
        if type_rapport in types:
            retenus.append(job)
    return retenus


def _lire_artefact(forge, projet_id: int, job_id: int, nom: str) -> dict | None:
    """Le rapport JSON d'un job, ou None s'il est introuvable ou illisible.

    DEUX CHEMINS, parce que le premier n'est pas garanti. Un rapport declare
    sous `artifacts:reports:` est range par GitLab comme un artefact TYPE ; selon
    la version, il figure aussi, ou non, dans l'archive que l'API sert sous
    `/artifacts/<chemin>`. On essaie d'abord le fichier par son chemin, puis on
    telecharge l'archive complete et on en extrait le fichier. Si les deux
    echouent, la fonction rend None et le test le dit : il ne conclut jamais
    sur une mesure absente.
    """
    brut = api(forge, f"/projects/{projet_id}/jobs/{job_id}/artifacts/{nom}", brut=True)
    if isinstance(brut, str):
        try:
            charge = json.loads(brut)
        except json.JSONDecodeError:
            charge = None
        if isinstance(charge, dict) and "vulnerabilities" in charge:
            return charge

    extraction = (
        "import sys, zipfile, io\n"
        "z = zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read()))\n"
        f"sys.stdout.write(z.read({nom!r}).decode())\n"
    )
    cmd = (
        'JETON=$(cat /etc/dsoxlab/jeton-api 2>/dev/null); [ -n "$JETON" ] || exit 64; '
        'curl -sS --fail --max-time 60 -H "PRIVATE-TOKEN: $JETON" '
        f"{shlex.quote(f'{URL}/api/v4/projects/{projet_id}/jobs/{job_id}/artifacts')} "
        f"| python3 -c {shlex.quote(extraction)}"
    )
    r = forge.run(cmd)
    if r.rc != 0 or not r.stdout.strip():
        return None
    try:
        charge = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    return charge if isinstance(charge, dict) else None


def _est_le_jeton_plante(trouvaille: dict) -> bool:
    """Cette trouvaille de Secret Detection designe-t-elle le jeton du setup ?

    Le projet fil rouge porte d'autres chaines qui ressemblent a un secret (une
    URL de base de donnees avec un mot de passe, par exemple). Le lab ne note
    que le jeton que le setup a plante : on le reconnait a son fichier, puis a
    son extrait de code ou, si l'extrait est masque, a sa regle.
    """
    emplacement = trouvaille.get("location") or {}
    chemin = str(emplacement.get("file") or "")
    if not chemin.endswith(FICHIER_DEFAUT):
        return False
    extrait = str(trouvaille.get("raw_source_code_extract") or "")
    if MOTIF_JETON.search(extrait):
        return True
    texte = json.dumps(trouvaille).lower()
    return any(signature in texte for signature in SIGNATURES_JETON)


def _rapports_secrets(forge, projet_id: int, liste_pipelines: list):
    """Pour chaque pipeline, ses rapports Secret Detection lisibles.

    Rend des triplets (pipeline, job, rapport). Les rapports illisibles sont
    ignores ici : c'est le test appelant qui dit pourquoi il n'a rien trouve.
    """
    for pipeline in liste_pipelines:
        for job in _jobs_avec_rapport(forge, projet_id, pipeline, TYPE_SECRETS):
            rapport = _lire_artefact(forge, projet_id, job["id"], NOM_SECRETS)
            if rapport is not None:
                yield pipeline, job, rapport


def test_sast_a_tourne_et_depose_son_rapport(forge, projet_du_lab, pipelines_main):
    """SAST a vraiment tourne : un job reussi, un artefact de type `sast`.

    Mesure le travail de base du lab : activer le scanner de code. Le pipeline
    de depart n'a qu'un job de test, donc aucun artefact `sast` : ce test ne
    peut pas etre vert avant que le lecteur ait inclus le template ET que le
    job ait tourne jusqu'au bout.

    Il lit aussi le contenu : un rapport valide porte `scan.type == "sast"` et
    une liste `vulnerabilities`. Cette liste peut etre VIDE sur une petite
    application, et c'est un resultat valide : le test n'exige aucune
    trouvaille, il exige un scan mene a son terme.
    """
    candidats = []
    for pipeline in pipelines_main:
        candidats += [(pipeline, j) for j in _jobs_avec_rapport(forge, projet_du_lab["id"], pipeline, TYPE_SAST)]
    assert candidats, message(
        en=(
            "No successful job of the last pipelines on main produced a SAST "
            "report (an artifact of type `sast`). A template in `include:` is "
            "not a report: the job has to run to the end. Add "
            "`include: - template: Jobs/SAST.gitlab-ci.yml` to .gitlab-ci.yml, "
            "push, and wait for the pipeline. Without it, the code is never "
            "analysed and nobody learns what it contains."
        ),
        fr=(
            "Aucun job réussi des derniers pipelines de main n'a produit de "
            "rapport SAST (un artefact de type `sast`). Un template dans "
            "`include:` n'est pas un rapport : le job doit aller au bout. "
            "Ajoutez `include: - template: Jobs/SAST.gitlab-ci.yml` à "
            ".gitlab-ci.yml, poussez, et attendez le pipeline. Sans cela, le "
            "code n'est jamais analysé et personne n'apprend ce qu'il contient."
        ),
    )

    pipeline, job = candidats[0]
    rapport = _lire_artefact(forge, projet_du_lab["id"], job["id"], NOM_SAST)
    assert rapport is not None, message(
        en=(
            f"Job {job.get('name')} (pipeline {pipeline['id']}) declares a SAST "
            f"report, but {NOM_SAST} could not be read from its artifacts. "
            "Open the job page and check that its artifacts were kept (they "
            "expire), then re-run the pipeline."
        ),
        fr=(
            f"Le job {job.get('name')} (pipeline {pipeline['id']}) déclare un "
            f"rapport SAST, mais {NOM_SAST} n'a pas pu être lu dans ses "
            "artefacts. Ouvrez la page du job, vérifiez que ses artefacts sont "
            "conservés (ils expirent), puis relancez le pipeline."
        ),
    )
    scan = rapport.get("scan") or {}
    assert scan.get("type") == TYPE_SAST and isinstance(rapport.get("vulnerabilities"), list), (
        message(
            en=(
                f"{NOM_SAST} is readable but is not a SAST report: expected "
                '`scan.type` = "sast" and a `vulnerabilities` list.'
            ),
            fr=(
                f"{NOM_SAST} est lisible mais n'est pas un rapport SAST : on "
                'attend `scan.type` = "sast" et une liste `vulnerabilities`.'
            ),
        )
    )


def test_secret_detection_a_tourne_et_depose_son_rapport(forge, projet_du_lab, pipelines_main):
    """Secret Detection a vraiment tourne : un job reussi, un artefact `secret_detection`.

    Meme exigence que pour SAST, sur l'autre scanner du lab. Le pipeline de
    depart ne produit aucun artefact de ce type : ce test est rouge au depart.

    Il exige un rapport LISIBLE, de type `secret_detection`. Il n'exige pas
    encore qu'il contienne quelque chose : le test suivant mesure que le
    defaut plante a ete vu.
    """
    rapports = list(_rapports_secrets(forge, projet_du_lab["id"], pipelines_main))
    if not rapports:
        # Distinguer « jamais tourne » de « a tourne mais illisible » : le
        # message n'envoie pas l'apprenant au meme endroit.
        a_tourne = any(
            _jobs_avec_rapport(forge, projet_du_lab["id"], p, TYPE_SECRETS) for p in pipelines_main
        )
        assert a_tourne, message(
            en=(
                "No successful job of the last pipelines on main produced a "
                "Secret Detection report (an artifact of type "
                "`secret_detection`). Add `include: - template: "
                "Jobs/Secret-Detection.gitlab-ci.yml` to .gitlab-ci.yml, push, "
                "and wait for the pipeline. Without it, a committed token "
                "stays invisible until someone abuses it."
            ),
            fr=(
                "Aucun job réussi des derniers pipelines de main n'a produit de "
                "rapport Secret Detection (un artefact de type "
                "`secret_detection`). Ajoutez `include: - template: "
                "Jobs/Secret-Detection.gitlab-ci.yml` à .gitlab-ci.yml, "
                "poussez, et attendez le pipeline. Sans cela, un jeton commité "
                "reste invisible jusqu'à ce que quelqu'un en abuse."
            ),
        )
        pytest.fail(
            message(
                en=(
                    f"A Secret Detection job ran, but {NOM_SECRETS} could not be "
                    "read from its artifacts (they may have expired). Re-run "
                    "the pipeline."
                ),
                fr=(
                    f"Un job Secret Detection a tourné, mais {NOM_SECRETS} n'a "
                    "pas pu être lu dans ses artefacts (ils ont peut-être "
                    "expiré). Relancez le pipeline."
                ),
            )
        )

    _pipeline, _job, rapport = rapports[0]
    scan = rapport.get("scan") or {}
    assert scan.get("type") == TYPE_SECRETS and isinstance(rapport.get("vulnerabilities"), list), (
        message(
            en=(
                f"{NOM_SECRETS} is readable but is not a Secret Detection "
                'report: expected `scan.type` = "secret_detection" and a '
                "`vulnerabilities` list."
            ),
            fr=(
                f"{NOM_SECRETS} est lisible mais n'est pas un rapport Secret "
                'Detection : on attend `scan.type` = "secret_detection" et une '
                "liste `vulnerabilities`."
            ),
        )
    )


def test_un_scan_a_vu_le_jeton_ecrit_en_dur(forge, projet_du_lab, pipelines_main):
    """Le defaut a ete TROUVE PAR UN SCAN, pas par une lecture du code.

    Le setup a ecrit un jeton GitLab fabrique dans `app/config.py`. Le lab ne
    note pas seulement qu'il disparait : il exige qu'un rapport l'ait designe.
    Sinon on ne mesure pas l'outil, on mesure une relecture du fichier, et un
    apprenant qui efface la ligne sans activer le scanner aurait tout reussi.

    CE TEST PEUT EXIGER LE SCAN HISTORIQUE, et c'est voulu. Le jeton est dans
    un commit ANTERIEUR a celui qui active le scanner. Selon la version, un scan
    de branche n'examine que les commits qu'il vient de recevoir : il ne voit
    alors pas ce jeton. La lecon enseigne la parade, un pipeline lance a la
    main avec `SECRET_DETECTION_HISTORIC_SCAN` a `"true"`, et le test cherche
    le jeton dans TOUS les rapports des pipelines recents de `main`, quelle
    qu'en soit l'origine.
    """
    vus = []
    for _pipeline, _job, rapport in _rapports_secrets(forge, projet_du_lab["id"], pipelines_main):
        vus += [v for v in rapport.get("vulnerabilities") or [] if _est_le_jeton_plante(v)]

    assert vus, message(
        en=(
            f"No Secret Detection report of the last pipelines on main points "
            f"at the token written in {FICHIER_DEFAUT}. Either the scanner has "
            "not run yet, or it only looked at the commits of your last push "
            "and the token sits in an earlier one. Run a ONE-OFF pipeline "
            "(Build > Pipelines > New pipeline, branch main) with the variable "
            "SECRET_DETECTION_HISTORIC_SCAN = true, then read the report. Do "
            "not leave that variable in .gitlab-ci.yml: it lengthens every "
            "pipeline."
        ),
        fr=(
            f"Aucun rapport Secret Detection des derniers pipelines de main ne "
            f"désigne le jeton écrit dans {FICHIER_DEFAUT}. Soit le scanner n'a "
            "pas encore tourné, soit il n'a regardé que les commits de votre "
            "dernier push et le jeton est dans un commit antérieur. Lancez un "
            "pipeline UNIQUE (Build > Pipelines > New pipeline, branche main) "
            "avec la variable SECRET_DETECTION_HISTORIC_SCAN = true, puis lisez "
            "le rapport. Ne laissez pas cette variable dans .gitlab-ci.yml : "
            "elle rallonge tous les pipelines."
        ),
    )


def test_le_jeton_est_retire_et_un_nouveau_scan_le_confirme(forge, projet_du_lab):
    """Le defaut est corrige, et c'est un NOUVEAU SCAN qui le constate.

    Trois conditions, toutes sur l'etat de la forge, aucune sur les commandes :

      1. `app/config.py` existe encore sur `main` et ne contient plus le
         jeton. Le fichier ne doit pas avoir ete supprime : l'application en
         depend (`from app.config import settings`) ;
      2. un pipeline de PUSH a ete lance sur le DERNIER commit de `main`, et
         son rapport Secret Detection ne designe plus le jeton. Un pipeline
         lance a la main ne compte pas ici : il peut etre un scan historique,
         qui revoit tout le passe et trouvera toujours un jeton qu'on ne peut
         pas « decommiter » ;
      3. ce pipeline est sain : aucun job en echec ni annule, et au moins un job
         qui n'est pas un scanner a reussi (le test de l'application tourne
         toujours).

    Ce test ne mesure pas que le secret a ete REVOQUE, ce qui ne se lit nulle
    part : la lecon le dit, le scenario le rappelle. Retirer la ligne ne
    suffit pas, le jeton reste dans l'historique.

    IL NE PEUT PAS ETRE VERT AU DEPART : le jeton est dans le fichier, et
    aucun pipeline de scan n'existe.
    """
    contenu = fichier(forge, FICHIER_DEFAUT, "main", projet_du_lab["id"])
    assert contenu is not None, message(
        en=(
            f"{FICHIER_DEFAUT} no longer exists on main. The application "
            "imports it: remove the token from the file, do not delete the file."
        ),
        fr=(
            f"{FICHIER_DEFAUT} n'existe plus sur main. L'application l'importe : "
            "retirez le jeton du fichier, ne supprimez pas le fichier."
        ),
    )
    assert not MOTIF_JETON.search(contenu), message(
        en=(
            f"{FICHIER_DEFAUT} on main still contains the GitLab token. Read "
            'it from the environment without a default value: os.getenv("REGISTRY_TOKEN", "") '
            "or os.environ.get(...), and give the real value to the pipeline "
            "through a CI/CD variable. Then push."
        ),
        fr=(
            f"{FICHIER_DEFAUT} sur main contient encore le jeton GitLab. Lisez-le "
            'dans l\'environnement sans valeur par défaut : os.getenv("REGISTRY_TOKEN", "") '
            "ou os.environ.get(...), et donnez la vraie valeur au pipeline par "
            "une variable CI/CD. Puis poussez."
        ),
    )

    branche = api(forge, f"/projects/{projet_du_lab['id']}/repository/branches/main")
    sha = (branche or {}).get("commit", {}).get("id") if isinstance(branche, dict) else None
    assert sha, message(
        en="The last commit of main could not be read from the API.",
        fr="Le dernier commit de main n'a pas pu être lu dans l'API.",
    )

    recents = pipelines(forge, ref="main", projet_id=projet_du_lab["id"])
    du_dernier_commit = [p for p in recents if p.get("sha") == sha and p.get("source") == "push"]
    assert du_dernier_commit, message(
        en=(
            "No push pipeline exists for the last commit of main. Either the "
            "fix is not pushed, or its pipeline has not been created yet. A "
            "fix that no scan has confirmed is only a claim."
        ),
        fr=(
            "Aucun pipeline de push n'existe pour le dernier commit de main. "
            "Soit la correction n'est pas poussée, soit son pipeline n'est pas "
            "encore créé. Une correction qu'aucun scan n'a confirmée n'est "
            "qu'une affirmation."
        ),
    )
    pipeline = du_dernier_commit[0]

    jobs_du_pipeline = jobs(forge, pipeline["id"], projet_du_lab["id"])
    en_echec = sorted(j.get("name") for j in jobs_du_pipeline if j.get("status") in ECHECS)
    assert not en_echec, message(
        en=(
            f"These jobs failed in the pipeline of the last commit: {en_echec}. "
            "A scanner that fails confirms nothing, and the application must "
            "still pass its tests."
        ),
        fr=(
            f"Ces jobs ont échoué dans le pipeline du dernier commit : "
            f"{en_echec}. Un scanner en échec ne confirme rien, et "
            "l'application doit toujours passer ses tests."
        ),
    )

    def _est_scanner(job: dict) -> bool:
        types = {a.get("file_type") for a in (job.get("artifacts") or []) if isinstance(a, dict)}
        return bool(types & {TYPE_SAST, TYPE_SECRETS})

    tests_ok = [j for j in jobs_du_pipeline if j.get("status") == "success" and not _est_scanner(j)]
    assert tests_ok, message(
        en=(
            "In the pipeline of the last commit, no job other than a scanner "
            "succeeded. The application test job must still run and pass."
        ),
        fr=(
            "Dans le pipeline du dernier commit, aucun job autre qu'un scanner "
            "n'a réussi. Le job de test de l'application doit toujours tourner "
            "et passer."
        ),
    )

    rapports = [
        (j, r)
        for p, j, r in _rapports_secrets(forge, projet_du_lab["id"], [pipeline])
    ]
    assert rapports, message(
        en=(
            "The pipeline of the last commit has no readable Secret Detection "
            "report: the scanner is no longer in .gitlab-ci.yml, or it has not "
            "finished. Keep the scanner on, and wait for the pipeline."
        ),
        fr=(
            "Le pipeline du dernier commit n'a aucun rapport Secret Detection "
            "lisible : le scanner n'est plus dans .gitlab-ci.yml, ou il n'a "
            "pas fini. Gardez le scanner actif et attendez le pipeline."
        ),
    )
    encore = [v for _, r in rapports for v in (r.get("vulnerabilities") or []) if _est_le_jeton_plante(v)]
    assert not encore, message(
        en=(
            f"The scan of the last commit still reports the token ({len(encore)} "
            "finding(s)). Check that no copy is left in another file, and that "
            "SECRET_DETECTION_HISTORIC_SCAN is not set in .gitlab-ci.yml: it "
            "makes every pipeline re-read the history, where the token will "
            "always be."
        ),
        fr=(
            f"Le scan du dernier commit signale encore le jeton ({len(encore)} "
            "trouvaille(s)). Vérifiez qu'aucune copie ne reste dans un autre "
            "fichier, et que SECRET_DETECTION_HISTORIC_SCAN n'est pas posée "
            "dans .gitlab-ci.yml : elle fait relire l'historique à chaque "
            "pipeline, et le jeton y sera toujours."
        ),
    )


def test_la_lecture_du_rapport_est_consignee(forge, projet_du_lab, pipelines_main):
    """La lecture du rapport est consignee dans `LECTURE.md`, a la racine de `main`.

    « Lire un rapport » est le geste central du lab, et un geste de lecture ne
    laisse aucune trace : un apprenant qui ne regarde que le resultat du job
    n'a rien lu. Le lab demande donc un court fichier qui nomme ce que le
    rapport a designe : le fichier ET la ligne. Le test relit le rapport pour
    connaitre la vraie ligne, il ne l'impose pas d'avance : si le setup bouge
    une ligne un jour, le test suit.

    Ce que le test ne juge pas : la qualite de la phrase, ni l'avis du lecteur
    sur la gravite. Il mesure que ce que le rapport a dit est bien recopie, pas
    que le lecteur l'a compris. C'est une trace de lecture, pas une preuve de
    comprehension.

    IL NE PEUT PAS ETRE VERT AU DEPART : `LECTURE.md` n'existe pas, et aucun
    rapport n'existe pour en tirer la ligne.
    """
    lignes = set()
    for _, _, rapport in _rapports_secrets(forge, projet_du_lab["id"], pipelines_main):
        for v in rapport.get("vulnerabilities") or []:
            if _est_le_jeton_plante(v):
                debut = (v.get("location") or {}).get("start_line")
                if isinstance(debut, int):
                    lignes.add(debut)
    assert lignes, message(
        en=(
            "No Secret Detection report points at the planted token yet, so "
            "there is no line to report. Do the previous steps first."
        ),
        fr=(
            "Aucun rapport Secret Detection ne désigne encore le jeton planté : "
            "il n'y a donc pas de ligne à consigner. Faites d'abord les étapes "
            "précédentes."
        ),
    )

    note = fichier(forge, "LECTURE.md", "main", projet_du_lab["id"])
    assert note is not None, message(
        en=(
            "LECTURE.md does not exist at the root of main. Create it and "
            f"write down what the report said: the file ({FICHIER_DEFAUT}) and "
            f"the line number. A report nobody has written down is a report "
            "nobody has read."
        ),
        fr=(
            "LECTURE.md n'existe pas à la racine de main. Créez-le et notez ce "
            f"que le rapport a dit : le fichier ({FICHIER_DEFAUT}) et le numéro "
            "de ligne. Un rapport que personne n'a consigné est un rapport que "
            "personne n'a lu."
        ),
    )
    assert FICHIER_DEFAUT in note, message(
        en=f"LECTURE.md does not name the file the report pointed at ({FICHIER_DEFAUT}).",
        fr=f"LECTURE.md ne nomme pas le fichier que le rapport désignait ({FICHIER_DEFAUT}).",
    )
    nombres = {int(n) for n in re.findall(r"\b\d+\b", note)}
    assert nombres & lignes, message(
        en=(
            f"LECTURE.md does not give the line the report pointed at. The "
            f"report says line {sorted(lignes)}; write that number in the file."
        ),
        fr=(
            f"LECTURE.md ne donne pas la ligne que le rapport désignait. Le "
            f"rapport dit ligne {sorted(lignes)} : écrivez ce numéro dans le fichier."
        ),
    )
