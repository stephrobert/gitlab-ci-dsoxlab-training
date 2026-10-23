"""Tests de l'epreuve gl-ep4-un-pipeline-a-industrialiser.

L'EPREUVE DE FIN DU NIVEAU c3. Le niveau s'appelle « Industrialiser » : ecrire
un pipeline qui marche ne suffit plus, il doit se factoriser, aller vite, se
relancer sans rien masquer et se deployer sans collision.

CE QUI LA DISTINGUE DE gl-19. Ce lab-la CONSTRUIT un pipeline depuis un cahier
des charges, avec trois indices payants. Ici le pipeline EXISTE, il est vert, et
cinq defauts ne sont pas nommes : c'est un DIAGNOSTIC.

CINQ DEFAUTS, et aucun job n'echoue pour autant :

  1. trois jobs recopient le meme preambule ;
  2. les tests tournent a la suite dans UN job, et les etapes s'attendent ;
  3. un pipeline enfant est genere mais son fichier n'est pas un artefact ;
  4. `retry: 2` rejoue n'importe quel echec, y compris celui du script ;
  5. le deploiement n'a ni verrou ni limite de duree.

CE QUI EST NOTE RESTE UN ETAT, lu dans l'API : la configuration telle que GitLab
l'a compilee, les jobs et rapports du dernier pipeline de `main`, ses pipelines
enfants et les verrous de deploiement. Aucun test ne lit un fichier du depot.

L'echec transitoire est INJECTE PAR LE DEPART : un job `sync-externe` refuse sa
premiere tentative avec le code 75, puis accepte. Seule une relance CIBLEE
l'absorbe (par code de sortie), et la relance de tout echec, y compris celle du
script, est precisement ce que l'epreuve refuse.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from gitlab import (  # noqa: E402
    HOTE,
    api,
    forge_joignable,
    lint_configuration,
    pipelines,
    projet,
)

from conftest import lab_host, message  # noqa: E402

TITRE_DEPART = "feat: pipeline de depart"
# Les raisons qu'une relance peut couvrir sans masquer un defaut du code.
REFUSEES = {"always", "script_failure", "unknown_failure"}
RESERVES = {"stages", "workflow", "default", "variables", "include"}


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
def rapport_lint(forge, projet_du_lab):
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
    return rapport


@pytest.fixture(scope="module")
def configuration(rapport_lint):
    """La configuration de `main` TELLE QUE GITLAB L'A COMPILEE."""
    return yaml.safe_load(rapport_lint["merged_yaml"])


@pytest.fixture(scope="module")
def dernier(forge, projet_du_lab):
    """Le dernier pipeline de main, ses jobs (relances comprises) et ses ponts."""
    tous = pipelines(forge, ref="main", projet_id=projet_du_lab["id"])
    assert tous, message(
        en="No pipeline on the default branch: push your configuration.",
        fr="Aucun pipeline sur la branche par défaut : poussez votre configuration.",
    )
    p = tous[0]
    base = f"/projects/{projet_du_lab['id']}/pipelines/{p['id']}"
    tentatives = api(forge, f"{base}/jobs", "per_page=100&include_retried=true")
    ponts = api(forge, f"{base}/bridges", "per_page=100")
    commit = api(forge, f"/projects/{projet_du_lab['id']}/repository/commits/{p['sha']}")
    tentatives = tentatives if isinstance(tentatives, list) else []
    # Une relance garde le meme nom : on ne retient que la derniere tentative.
    finales: dict[str, dict] = {}
    for j in sorted(tentatives, key=lambda x: x["id"]):
        finales[j["name"]] = j
    return {
        "pipeline": p,
        "tentatives": tentatives,
        "finales": finales,
        "ponts": ponts if isinstance(ponts, list) else [],
        "titre": (commit or {}).get("title", "") if isinstance(commit, dict) else "",
    }


def _jobs_visibles(configuration: dict) -> dict:
    return {
        nom: corps
        for nom, corps in configuration.items()
        if isinstance(corps, dict) and nom not in RESERVES and not str(nom).startswith(".")
    }


def _effectif(configuration: dict, corps: dict, cle: str):
    if cle in corps:
        return corps[cle]
    return (configuration.get("default") or {}).get(cle)


def _retry(configuration: dict, corps: dict) -> dict | None:
    brut = _effectif(configuration, corps, "retry")
    if brut is None:
        return None
    if isinstance(brut, int):
        brut = {"max": brut}
    when = brut.get("when")
    if isinstance(when, str):
        when = [when]
    return {"max": brut.get("max", 0), "when": when, "exit_codes": brut.get("exit_codes")}


def _cible(r: dict) -> bool:
    """Une relance est CIBLEE si elle nomme ses causes, et jamais le script."""
    if r["max"] <= 0 or r["max"] > 2:
        return False
    if r["when"] is None and not r["exit_codes"]:
        return False  # sans `when`, GitLab rejoue TOUT (« always »)
    return not (set(r["when"] or []) & REFUSEES)


def _instant(valeur):
    return datetime.fromisoformat(valeur.replace("Z", "+00:00")) if valeur else None


def test_la_configuration_est_factorisee(rapport_lint, configuration):
    """PREMIER DEFAUT : un preambule recopie trois fois.

    Le depart repete l'image, la preparation et les reglages dans trois jobs.
    Factoriser, c'est ecrire cela UNE fois : un fichier inclus, un composant,
    ou des `extends` sur un job cache. Le test lit la configuration compilee et
    refuse deux choses : l'absence de tout mecanisme de partage, et le
    meme `before_script` encore recopie dans trois jobs.
    """
    jobs = _jobs_visibles(configuration)
    inclus = rapport_lint.get("includes") or []
    etendus = [n for n, c in jobs.items() if c.get("extends")]
    assert inclus or len(etendus) >= 2, message(
        en=(
            "Nothing in the compiled configuration is shared: no include, no "
            "component, and fewer than two jobs extend a common definition. "
            "Every job still carries its own copy of the same lines."
        ),
        fr=(
            "Rien n'est partagé dans la configuration compilée : ni include, ni "
            "composant, et moins de deux jobs étendent une définition commune. "
            "Chaque job porte encore sa propre copie des mêmes lignes."
        ),
    )
    copies: dict[str, list[str]] = {}
    for nom, corps in jobs.items():
        # GitLab recopie dans le job etendu ce qu'il herite : seul un job qui
        # n'etend rien porte une copie qui lui est propre.
        avant = corps.get("before_script")
        if avant and not corps.get("extends"):
            copies.setdefault(yaml.safe_dump(avant), []).append(nom)
    repetes = {tuple(v) for v in copies.values() if len(v) >= 3}
    assert not repetes, message(
        en=(
            f"The same before_script is still copied in these jobs: {sorted(repetes)}. "
            "Sharing something is not enough if the duplication stays."
        ),
        fr=(
            f"Le même before_script est encore recopié dans ces jobs : {sorted(repetes)}. "
            "Partager quelque chose ne suffit pas si la duplication reste."
        ),
    )


def test_les_jobs_forment_un_graphe(configuration, dernier):
    """DEUXIEME DEFAUT, premiere moitie : les etapes s'attendent.

    Sans `needs`, un job attend la fin de TOUTE l'etape precedente, meme s'il
    n'a besoin de rien. Le test lit deux choses : des `needs` dans la
    configuration, et un fait dans le dernier pipeline, un job qui a demarre
    avant la fin d'un job d'une etape plus ancienne.
    """
    jobs = _jobs_visibles(configuration)
    avec_needs = [n for n, c in jobs.items() if "needs" in c]
    assert len(avec_needs) >= 2, message(
        en=(
            f"Only {len(avec_needs)} job(s) declare `needs`. Without a "
            "dependency graph, every stage waits for the whole previous one."
        ),
        fr=(
            f"Seulement {len(avec_needs)} job(s) déclarent `needs`. Sans graphe de "
            "dépendances, chaque étape attend la précédente en entier."
        ),
    )
    etapes = configuration.get("stages") or []
    finales = dernier["finales"]
    avance = []
    for a in finales.values():
        for b in finales.values():
            if a["stage"] not in etapes or b["stage"] not in etapes:
                continue
            if etapes.index(b["stage"]) < etapes.index(a["stage"]):
                debut, fin = _instant(a.get("started_at")), _instant(b.get("finished_at"))
                if debut and fin and debut < fin:
                    avance.append((a["name"], b["name"]))
    assert avance, message(
        en=(
            "In the latest pipeline of main, no job started before the end of "
            "a job of an earlier stage: the graph exists on paper only."
        ),
        fr=(
            "Dans le dernier pipeline de main, aucun job n'a démarré avant la fin "
            "d'un job d'une étape plus ancienne : le graphe n'existe que sur le papier."
        ),
    )


def test_les_tests_tournent_en_matrice_avec_rapports(configuration, dernier):
    """DEUXIEME DEFAUT, seconde moitie : des tests en serie dans un seul job.

    Une matrice produit un job par combinaison, nommes `job: [valeur]`. Le test
    exige au moins deux instances reussies, chacune avec un rapport de test
    NON VIDE : un fichier garde en simple `paths` n'est pas un rapport lu par
    GitLab, seul `reports: junit` produit l'artefact de type `junit`.
    """
    groupes: dict[str, list[dict]] = {}
    for j in dernier["finales"].values():
        if ": [" in j["name"]:
            groupes.setdefault(j["name"].split(": [")[0], []).append(j)
    matrices = {n: lst for n, lst in groupes.items() if len(lst) >= 2}
    assert matrices, message(
        en=(
            "No matrix in the latest pipeline of main: no job exists in at "
            "least two instances. The suites still run one after the other."
        ),
        fr=(
            "Aucune matrice dans le dernier pipeline de main : aucun job n'existe "
            "en au moins deux instances. Les suites s'exécutent encore à la suite."
        ),
    )
    declare = [n for n in matrices if (_jobs_visibles(configuration).get(n) or {}).get("parallel")]
    assert declare, message(
        en="The instances do not come from a `parallel:matrix` declaration.",
        fr="Les instances ne viennent pas d'une déclaration `parallel:matrix`.",
    )
    for _nom, instances in matrices.items():
        mauvais = {
            j["name"]: j["status"]
            for j in instances
            if j["status"] != "success"
            or not any(
                a.get("file_type") == "junit" and (a.get("size") or 0) > 0
                for a in j.get("artifacts") or []
            )
        }
        assert not mauvais, message(
            en=(
                f"These matrix instances are not successful or report no "
                f"non-empty junit file: {mauvais}."
            ),
            fr=(
                f"Ces instances de la matrice n'ont pas réussi ou ne remontent aucun "
                f"fichier junit non vide : {mauvais}."
            ),
        )


def test_le_pipeline_enfant_vient_d_un_artefact(configuration, dernier):
    """TROISIEME DEFAUT : un enfant genere dont le fichier n'est pas declare.

    Un pipeline enfant dynamique est ecrit par un job, puis recupere comme
    ARTEFACT par le declencheur. Au depart, le job ecrit son fichier mais ne le
    declare pas, et le declencheur lit un fichier statique du depot. Le test lit
    le declencheur compile, puis l'etat du pipeline enfant.
    """
    declencheurs = {
        n: c["trigger"]
        for n, c in _jobs_visibles(configuration).items()
        if isinstance(c.get("trigger"), dict)
    }
    depuis_artefact = []
    for nom, t in declencheurs.items():
        inc = t.get("include")
        liste = inc if isinstance(inc, list) else [inc]
        if any(isinstance(x, dict) and x.get("artifact") for x in liste):
            depuis_artefact.append(nom)
    assert depuis_artefact, message(
        en=(
            "No trigger job builds its child pipeline from a job artifact: the "
            "child is a static file, so the generated one is never used."
        ),
        fr=(
            "Aucun job déclencheur ne construit son pipeline enfant depuis l'artefact "
            "d'un job : l'enfant est un fichier statique, le fichier généré ne sert à rien."
        ),
    )
    etats = {
        p["name"]: (p.get("downstream_pipeline") or {}).get("status") for p in dernier["ponts"]
    }
    ok = [n for n in depuis_artefact if etats.get(n) == "success"]
    assert ok, message(
        en=f"The child pipeline of {depuis_artefact} did not succeed: {etats}.",
        fr=f"Le pipeline enfant de {depuis_artefact} n'a pas réussi : {etats}.",
    )


def test_le_deploiement_est_verrouille_et_borne(forge, projet_du_lab, configuration):
    """CINQUIEME DEFAUT : deux deploiements peuvent se croiser, sans limite.

    Un `resource_group` fait attendre un deploiement tant que le precedent n'a
    pas fini, et `timeout` borne un job qui se bloquerait. Le test lit la
    configuration compilee pour chaque job qui cible un environnement, puis la
    route des verrous du projet : elle n'en liste un qu'apres sa premiere
    utilisation reelle.
    """
    cibles = {n: c for n, c in _jobs_visibles(configuration).items() if c.get("environment")}
    assert cibles, message(
        en="No job targets an environment any more: the deployment disappeared.",
        fr="Plus aucun job ne cible un environnement : le déploiement a disparu.",
    )
    sans_verrou = [n for n, c in cibles.items() if not c.get("resource_group")]
    assert not sans_verrou, message(
        en=f"These deployment jobs have no resource_group: {sans_verrou}. Two can run at once.",
        fr=f"Ces jobs de déploiement n'ont pas de resource_group : {sans_verrou}. Deux peuvent tourner en même temps.",
    )
    sans_limite = [n for n, c in cibles.items() if not _effectif(configuration, c, "timeout")]
    assert not sans_limite, message(
        en=f"These deployment jobs have no timeout: {sans_limite}. A stuck one holds the lock for the runner default.",
        fr=f"Ces jobs de déploiement n'ont pas de timeout : {sans_limite}. Un job bloqué garde le verrou jusqu'au défaut du runner.",
    )
    groupes = api(forge, f"/projects/{projet_du_lab['id']}/resource_groups")
    assert isinstance(groupes, list) and groupes, message(
        en="The forge lists no resource group: no deployment ran under a lock yet.",
        fr="La forge ne liste aucun groupe de ressources : aucun déploiement n'a encore tourné sous verrou.",
    )


def test_les_relances_sont_ciblees(configuration):
    """QUATRIEME DEFAUT : `retry: 2` rejoue tout, y compris le script.

    Sans `when`, une relance couvre TOUS les echecs : un test casse par le code
    finit par passer au hasard, et le defaut est masque. Une relance utile
    nomme ses causes (pannes de la plateforme) ou un code de sortie. Le test
    refuse toute relance non ciblee, et en exige au moins une ciblee.
    """
    jobs = _jobs_visibles(configuration)
    relances = {n: r for n, c in jobs.items() if (r := _retry(configuration, c)) is not None}
    larges = {n: r for n, r in relances.items() if not _cible(r)}
    assert not larges, message(
        en=(
            f"These jobs retry failures that are not infrastructure ones: {larges}. "
            "A retry on script_failure (or no `when` at all) hides real defects."
        ),
        fr=(
            f"Ces jobs relancent des échecs qui ne sont pas ceux de l'infrastructure : {larges}. "
            "Une relance sur script_failure (ou sans `when`) masque de vrais défauts."
        ),
    )
    assert relances, message(
        en="No job retries anything: a transient failure always turns the pipeline red.",
        fr="Aucun job ne se relance : un échec transitoire met toujours le pipeline au rouge.",
    )


def test_un_echec_transitoire_est_absorbe(configuration, dernier):
    """L'ECHEC INJECTE : le service externe refuse la premiere tentative.

    Il sort avec le code 75, que GitLab classe en `script_failure`. Le test
    cherche, dans le dernier pipeline, un job qui a echoue puis reussi, et
    exige que sa relance soit CIBLEE : la rattraper par un `retry` general
    ferait passer l'echec, mais pas le diagnostic.
    """
    par_nom: dict[str, list[dict]] = {}
    for j in sorted(dernier["tentatives"], key=lambda x: x["id"]):
        par_nom.setdefault(j["name"], []).append(j)
    absorbes = [
        n
        for n, t in par_nom.items()
        if len(t) >= 2 and t[-1]["status"] == "success" and all(x["status"] == "failed" for x in t[:-1])
    ]
    assert absorbes, message(
        en=(
            "No job of the latest pipeline failed then succeeded on a retry: the "
            "injected transient failure was not absorbed (or the pipeline was "
            "not replayed since the retry policy changed)."
        ),
        fr=(
            "Aucun job du dernier pipeline n'a échoué puis réussi après relance : "
            "l'échec transitoire injecté n'a pas été absorbé (ou le pipeline n'a pas "
            "été rejoué depuis le changement de politique de relance)."
        ),
    )
    jobs = _jobs_visibles(configuration)
    mal = [
        n
        for n in absorbes
        if n in jobs and (_retry(configuration, jobs[n]) is None or not _cible(_retry(configuration, jobs[n])))
    ]
    assert not mal, message(
        en=f"{mal} was absorbed by a retry that is not targeted: it would replay a script bug just the same.",
        fr=f"{mal} a été absorbé par une relance non ciblée : elle rejouerait tout aussi bien un bug du script.",
    )


def test_le_dernier_pipeline_est_vert_et_vient_de_l_apprenant(dernier):
    """LE GARDE-FOU DES CINQ AUTRES : tout a ete fait sans casser la chaine.

    Le pipeline de depart est deja vert, et un test qui ne mesurerait que cela
    serait vert avant tout travail. On exige donc un pipeline vert qui n'est
    pas celui du depart (autre commit), dont aucune derniere tentative n'est
    en echec, et dont le deploiement a eu lieu.
    """
    p = dernier["pipeline"]
    assert p["status"] == "success", message(
        en=f"The latest pipeline of main is {p['status']!r}: it must be green.",
        fr=f"Le dernier pipeline de main est {p['status']!r} : il doit être vert.",
    )
    assert dernier["titre"] != TITRE_DEPART, message(
        en="The latest pipeline is still the starting one: no change of yours has run on main.",
        fr="Le dernier pipeline est encore celui du départ : aucun de vos changements n'a tourné sur main.",
    )
    pas_reussis = {n: j["status"] for n, j in dernier["finales"].items() if j["status"] != "success"}
    assert not pas_reussis, message(
        en=f"These jobs did not succeed: {pas_reussis}.",
        fr=f"Ces jobs n'ont pas réussi : {pas_reussis}.",
    )
    deploye = [n for n, j in dernier["finales"].items() if (j.get("environment") or j.get("deployment"))]
    assert deploye or any("deploy" in n for n in dernier["finales"]), message(
        en="No deployment job ran in the latest pipeline.",
        fr="Aucun job de déploiement n'a tourné dans le dernier pipeline.",
    )
