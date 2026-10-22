"""Tests du lab gl-20-secrets-avances.

CE LAB NOTE L'ETAT QUE LA FORGE MONTRE, JAMAIS CE QUI EST ECRIT. Un
`.gitlab-ci.yml` qui parle d'une variable protegee ne prouve pas qu'elle l'est
cote serveur : seul l'API de GitLab le dit. Les tests lisent donc les reglages
des variables, l'etat des jetons d'acces, les jobs et les journaux.

LA REGLE DU CATALOGUE : l'etat de depart est un pipeline vert qui consomme deux
secrets mal geres. Chacun des quatre tests porte sur une absence que le setup
a mesuree, et aucun ne peut etre vert au depart :
  1. le jeton de service n'est ni protege ni masque ;
  2. la cle de deploiement est une variable ordinaire, pas un fichier ;
  3. le jeton de depart est toujours actif, et aucun pipeline n'a tourne
     depuis (le setup enregistre le dernier pipeline dans `depart-pipeline`) ;
  4. aucun pipeline n'a tourne depuis le depart, et le job de depart qui
     recevait la cle comme VALEUR echoue des qu'elle devient un chemin : il
     faut l'adapter, et le journal de `installer-la-cle` doit afficher
     `CLE-SOURCE=fichier`, ligne que le job de depart ecrit lui-meme.

SUJET ECARTE : la fuite d'un secret dans un journal est le sujet de
gl-05-sortir-les-secrets. Sur GitLab 19.5.1 le runner remplace tout jeton
`glpat-` par `glpat-[MASKED]` meme si la variable n'est pas masquee : un jeton
d'acces de projet ne peut pas fuir, ce lab ne le teste donc pas.

CE QUE LES TESTS NE FONT PAS. Ils n'imposent ni la facon de creer le jeton
(interface, API, route `rotate`), ni l'edition du pipeline. Ils imposent le
NOM des deux jobs de depart, qui doivent rester verts.

LIMITE ASSUMEE, A LIRE AVANT DE CROIRE AU MOT « SANS INTERRUPTION » : la
forge ne date pas la revocation d'un jeton. Un test ne peut donc pas prouver
que le nouveau jeton servait AVANT la revocation de l'ancien. Il mesure ce qui
est mesurable : l'ancien est revoque, la variable porte un autre jeton, actif,
et aucun job d'appel du service n'a echoue depuis le depart. Un apprenant qui
revoque d'abord et cree ensuite, sans lancer de pipeline entre les deux, ne
serait pas pris. Le scenario le dit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    URL,
    api,
    forge_joignable,
    jobs,
    pipelines,
    projet,
)

from conftest import lab_host, message  # noqa: E402

ETAT = "/var/lib/dsoxlab/gl-20"
JOB_SERVICE = "joindre-le-service"
JOB_CLE = "installer-la-cle"
ENCOURS = ("created", "pending", "running", "waiting_for_resource", "preparing")


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


def _fait(host, nom: str) -> int:
    """Un fait pose par le setup. Son absence est une panne du lab, pas de l'apprenant."""
    r = host.run(f"cat {ETAT}/{nom}")
    assert r.rc == 0 and r.stdout.strip().isdigit(), message(
        en=(
            f"The setup fact {ETAT}/{nom} is missing or unreadable. The lab setup "
            "did not complete: replay it with dsoxlab run."
        ),
        fr=(
            f"Le fait posé par le setup {ETAT}/{nom} est absent ou illisible. Le "
            "setup du lab n'est pas allé au bout : rejouez-le avec dsoxlab run."
        ),
    )
    return int(r.stdout.strip())


def _variable(forge, projet_id: int, nom: str) -> dict:
    v = api(forge, f"/projects/{projet_id}/variables/{nom}")
    assert isinstance(v, dict) and v.get("key") == nom, message(
        en=f"The variable {nom} no longer exists in the project: it must stay, with its settings fixed.",
        fr=f"La variable {nom} n'existe plus dans le projet : elle doit rester, avec ses réglages corrigés.",
    )
    return v


def _branche_protegee(forge, projet_id: int) -> bool:
    b = api(forge, f"/projects/{projet_id}/protected_branches/main")
    return isinstance(b, dict) and b.get("name") == "main"


def _depuis_le_depart(forge, projet_id: int, depart: int) -> list:
    """Les pipelines de `main` posterieurs au depart, du plus recent au plus ancien."""
    tous = pipelines(forge, ref="main", projet_id=projet_id)
    return sorted((p for p in tous if p["id"] > depart), key=lambda p: p["id"], reverse=True)


def _trace(host, projet_id: int, job_id: int) -> str:
    out = api(host, f"/projects/{projet_id}/jobs/{job_id}/trace", brut=True)
    return out if isinstance(out, str) else ""


def _jeton_de_la_variable(host, projet_id: int) -> dict | None:
    """Ce que la forge dit du jeton que porte SERVICE_TOKEN, ou None.

    Le script tourne SUR LA VM : il lit la valeur de la variable et la presente
    a la forge par l'entree standard (`curl -H @-`). La valeur ne figure donc
    sur aucune ligne de commande, ni dans le test, ni dans un `ps`. La route
    `personal_access_tokens/self` repond pour un jeton d'acces de projet comme
    pour un jeton personnel.
    """
    cmd = (
        'JETON=$(cat /etc/dsoxlab/jeton-api); '
        f'VAL=$(curl -sS --max-time 20 -H "PRIVATE-TOKEN: $JETON" '
        f'{URL}/api/v4/projects/{projet_id}/variables/SERVICE_TOKEN | jq -r ".value // empty"); '
        '[ -n "$VAL" ] || exit 65; '
        'printf "PRIVATE-TOKEN: %s\\n" "$VAL" | curl -sS --max-time 20 -H @- '
        f'{URL}/api/v4/personal_access_tokens/self'
    )
    r = host.run(cmd)
    if r.rc != 0:
        return None
    try:
        rep = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    return rep if isinstance(rep, dict) else None


def test_jeton_de_service_protege_et_masque(forge, projet_du_lab) -> None:
    """SERVICE_TOKEN est protegee ET masquee, sur une branche qui l'est aussi."""
    v = _variable(forge, projet_du_lab["id"], "SERVICE_TOKEN")
    assert v.get("protected") is True, message(
        en=(
            "SERVICE_TOKEN is not protected. A protected variable is only handed "
            "to pipelines of protected branches and tags: without it, any branch "
            "anyone can push reads the token."
        ),
        fr=(
            "SERVICE_TOKEN n'est pas protégée. Une variable protégée n'est remise "
            "qu'aux pipelines des branches et étiquettes protégées : sans cela, "
            "n'importe quelle branche que quelqu'un peut pousser lit le jeton."
        ),
    )
    assert v.get("masked") is True, message(
        en=(
            "SERVICE_TOKEN is not masked. A masked variable is replaced by "
            "[MASKED] in job logs, which anyone who sees the project can download."
        ),
        fr=(
            "SERVICE_TOKEN n'est pas masquée. Une variable masquée est remplacée "
            "par [MASKED] dans les journaux des jobs, que tout lecteur du projet "
            "peut télécharger."
        ),
    )
    assert _branche_protegee(forge, projet_du_lab["id"]), message(
        en=(
            "The main branch is no longer protected: a protected variable would "
            "never reach its pipelines. Protecting a variable only makes sense "
            "on a protected branch."
        ),
        fr=(
            "La branche main n'est plus protégée : une variable protégée ne "
            "parviendrait jamais à ses pipelines. Protéger une variable n'a de "
            "sens que sur une branche protégée."
        ),
    )


def test_cle_de_deploiement_en_fichier(forge, projet_du_lab) -> None:
    """DEPLOY_KEY est une variable de type fichier, protegee, et intacte."""
    v = _variable(forge, projet_du_lab["id"], "DEPLOY_KEY")
    assert v.get("variable_type") == "file", message(
        en=(
            f"DEPLOY_KEY has type {v.get('variable_type')!r}. A multi-line secret "
            "such as a key is a file-type variable: the job then receives the "
            "PATH of a file that holds the value, not the value itself."
        ),
        fr=(
            f"DEPLOY_KEY est de type {v.get('variable_type')!r}. Un secret sur "
            "plusieurs lignes comme une clé est une variable de type fichier : "
            "le job reçoit alors le CHEMIN d'un fichier qui porte la valeur, "
            "pas la valeur."
        ),
    )
    assert v.get("protected") is True, message(
        en="DEPLOY_KEY is not protected: any branch could read the deployment key.",
        fr="DEPLOY_KEY n'est pas protégée : n'importe quelle branche pourrait lire la clé de déploiement.",
    )
    valeur = v.get("value") or ""
    assert valeur.startswith("-----BEGIN OPENSSH PRIVATE KEY-----") and valeur.endswith("\n"), message(
        en=(
            "The value of DEPLOY_KEY was altered: it must stay the original key, "
            "ending with a newline (a file-type variable without a final newline "
            "is rejected by OpenSSH)."
        ),
        fr=(
            "La valeur de DEPLOY_KEY a été altérée : elle doit rester la clé "
            "d'origine, terminée par un retour à la ligne (une variable fichier "
            "sans retour final est refusée par OpenSSH)."
        ),
    )


def test_jeton_renouvele_sans_interruption(forge, projet_du_lab) -> None:
    """L'ancien jeton est revoque, la variable en porte un autre, et le service n'a jamais manque."""
    pid = projet_du_lab["id"]
    ancien_id = _fait(forge, "ancien-jeton-id")
    depart = _fait(forge, "depart-pipeline")

    ancien = api(forge, f"/projects/{pid}/access_tokens/{ancien_id}")
    assert isinstance(ancien, dict) and ancien.get("id") == ancien_id, message(
        en="The initial access token (service-v1) cannot be found: do not delete the project token list.",
        fr="Le jeton d'accès de départ (service-v1) est introuvable : ne supprimez pas la liste des jetons du projet.",
    )
    assert ancien.get("revoked") is True or ancien.get("active") is False, message(
        en=(
            "The old token service-v1 is still active. Renewing a secret is not "
            "adding a second one: the old one must be revoked once the new one "
            "serves, otherwise a leaked copy stays valid."
        ),
        fr=(
            "L'ancien jeton service-v1 est toujours actif. Renouveler un secret "
            "n'est pas en ajouter un second : l'ancien doit être révoqué une fois "
            "le nouveau en service, sinon une copie qui a fuité reste valable."
        ),
    )

    actuel = _jeton_de_la_variable(forge, pid)
    assert actuel is not None and actuel.get("id"), message(
        en=(
            "The value held by SERVICE_TOKEN is not accepted by the forge "
            f"(answer: {actuel}). The variable must carry a valid, active token."
        ),
        fr=(
            "La valeur que porte SERVICE_TOKEN n'est pas acceptée par la forge "
            f"(réponse : {actuel}). La variable doit porter un jeton valide et actif."
        ),
    )
    assert actuel["id"] != ancien_id and actuel.get("active") is True, message(
        en="SERVICE_TOKEN still holds the old token: put the NEW token in it.",
        fr="SERVICE_TOKEN porte encore l'ancien jeton : mettez-y le NOUVEAU jeton.",
    )

    apres = _depuis_le_depart(forge, pid, depart)
    echecs = []
    reussites_apres_le_nouveau = 0
    for p in apres:
        for j in jobs(forge, p["id"], pid):
            if j["name"] != JOB_SERVICE:
                continue
            if j["status"] in ("failed", "canceled"):
                echecs.append(f"pipeline {p['id']} : {j['status']}")
            elif j["status"] == "success" and (p.get("created_at") or "") >= (actuel.get("created_at") or "~"):
                reussites_apres_le_nouveau += 1
    assert not echecs, message(
        en=(
            f"The job {JOB_SERVICE} failed since the start ({'; '.join(echecs)}): "
            "the service was interrupted. Put the new token in the variable "
            "BEFORE revoking the old one."
        ),
        fr=(
            f"Le job {JOB_SERVICE} a échoué depuis le départ ({'; '.join(echecs)}) : "
            "le service a été interrompu. Mettez le nouveau jeton dans la variable "
            "AVANT de révoquer l'ancien."
        ),
    )
    assert reussites_apres_le_nouveau >= 1, message(
        en=(
            f"No pipeline has run {JOB_SERVICE} successfully with the new token "
            "yet. Run one: a renewed secret is only proved by a job that uses it."
        ),
        fr=(
            f"Aucun pipeline n'a encore exécuté {JOB_SERVICE} avec succès avec le "
            "nouveau jeton. Lancez-en un : un secret renouvelé ne se prouve que par "
            "un job qui s'en sert."
        ),
    )


def test_dernier_pipeline_sain_et_cle_lue_en_fichier(forge, projet_du_lab) -> None:
    """Le dernier pipeline de main est sain, et le job a lu la cle depuis un fichier."""
    pid = projet_du_lab["id"]
    depart = _fait(forge, "depart-pipeline")
    apres = _depuis_le_depart(forge, pid, depart)
    assert apres, message(
        en="No pipeline has run on main since the lab started: push a change or run one.",
        fr="Aucun pipeline n'a tourné sur main depuis le début du lab : poussez un changement ou lancez-en un.",
    )
    dernier = apres[0]
    assert dernier.get("status") not in ENCOURS, message(
        en=f"The latest pipeline is still {dernier.get('status')}. Wait for it, then run the check again.",
        fr=f"Le dernier pipeline est encore {dernier.get('status')}. Attendez-le, puis relancez la vérification.",
    )
    liste = jobs(forge, dernier["id"], pid)
    par_nom = {j["name"]: j for j in liste}
    mauvais = [f"{j['name']} ({j['status']})" for j in liste if j["status"] in ("failed", "canceled")]
    assert not mauvais, message(
        en=(
            f"The latest pipeline has failed jobs: {', '.join(mauvais)}. Read their "
            "logs. If it is installer-la-cle after turning DEPLOY_KEY into a file, "
            "the job still treats the variable as a value: it now holds a PATH."
        ),
        fr=(
            f"Le dernier pipeline a des jobs en échec : {', '.join(mauvais)}. Lisez "
            "leurs journaux. S'il s'agit de installer-la-cle après le passage de "
            "DEPLOY_KEY en fichier, le job traite encore la variable comme une "
            "valeur : elle porte désormais un CHEMIN."
        ),
    )
    for nom in (JOB_SERVICE, JOB_CLE):
        assert nom in par_nom and par_nom[nom]["status"] == "success", message(
            en=f"The job {nom} must exist and pass in the latest pipeline of main.",
            fr=f"Le job {nom} doit exister et réussir dans le dernier pipeline de main.",
        )
    trace = _trace(forge, pid, par_nom[JOB_CLE]["id"])
    assert "CLE-SOURCE=fichier" in trace, message(
        en=(
            f"The log of {JOB_CLE} does not show CLE-SOURCE=fichier. Either the "
            "latest pipeline ran before DEPLOY_KEY became a file-type variable "
            "(run a new one), or the CLE-SOURCE line of the starting job was "
            "removed: keep it while adapting the job."
        ),
        fr=(
            f"Le journal de {JOB_CLE} n'affiche pas CLE-SOURCE=fichier. Soit le "
            "dernier pipeline a tourné avant que DEPLOY_KEY ne devienne une "
            "variable de type fichier (lancez-en un nouveau), soit la ligne "
            "CLE-SOURCE du job de départ a été retirée : conservez-la en "
            "adaptant le job."
        ),
    )
