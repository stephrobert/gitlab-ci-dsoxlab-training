"""Tests du lab gl-04-artifacts-et-cache.

LE PIPELINE DE DEPART EST DEJA VERT, ce qui change la nature de ce lab : il n'y
a rien a reparer, il y a du gaspillage a supprimer et un resultat a rendre
exploitable. Les tests notent donc deux choses que l'etat de depart ne porte
pas, et AUCUN d'eux ne se contente de verifier le vert : un tel test passerait
avant tout travail, et ne mesurerait que l'hypothese du setup.

PREMIEREMENT, LE RAPPORT DE TESTS. Un artefact depose dans le pipeline ne
suffit pas : GitLab doit l'avoir INTERPRETE, ce qui n'arrive qu'avec
`reports: junit:`. La preuve ne se lit pas dans la liste des artefacts, elle se
lit dans le rapport de tests du pipeline, que l'API sert sur
`/pipelines/:id/test_report`. Un `paths:` sans `reports:` donne un fichier
telechargeable et un onglet Tests vide.

DEUXIEMEMENT, LE CACHE DOIT SERVIR, pas seulement etre declare. Un cache
declare se cree au premier passage et ne se restaure qu'au suivant : un lab qui
se contenterait de voir « Creating cache » noterait une intention. On exige donc
qu'un cache ait ete RESTAURE, ce qui demande deux passages, et c'est
exactement ce que le lab fait constater a l'apprenant.

CE QU'ON NE VERIFIE PAS : ni le nom des jobs, ni la cle du cache, ni le chemin
mis en cache. Un apprenant qui met en cache le repertoire de pip par un autre
chemin a fait le travail.
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
    return {"projet": p, "pipeline": dernier}


@pytest.fixture(scope="module")
def traces_du_dernier(forge, contexte):
    """Les journaux du DERNIER pipeline, concatenes.

    Un seul relevé pour plusieurs tests : chaque journal coute un appel a
    l'API depuis la VM.
    """
    tous = jobs(forge, contexte["pipeline"]["id"], contexte["projet"]["id"])
    morceaux = []
    for j in tous:
        brut = api(
            forge,
            f"/projects/{contexte['projet']['id']}/jobs/{j['id']}/trace",
            brut=True,
        )
        if brut:
            morceaux.append(brut.lower())
    return "\n".join(morceaux)


def test_les_resultats_de_tests_sont_lisibles_dans_gitlab(forge, contexte):
    """GitLab doit avoir INTERPRETE le rapport, pas seulement garde un fichier.

    `paths:` rend le fichier telechargeable ; seul `reports: junit:` remplit le
    rapport de tests du pipeline. C'est la difference que ce test mesure, et
    c'est tout le sujet d'un artefact de rapport.

    IL N'Y A PAS DE TEST « LE PIPELINE EST VERT » DANS CE LAB, et c'est une
    correction, pas un oubli. Ce lab part d'un pipeline DEJA VERT : un tel test
    passait donc avant tout travail, ce que `valider-labs.py` a refuse a juste
    titre (« un test vert sur l'etat de depart n'est pas un test, c'est une
    hypothese du setup »). L'exigence du vert est donc portee ici, par le test
    qui mesure quelque chose que l'etat de depart ne porte pas : on ne gagne
    pas un rapport lisible en cassant le pipeline.
    """
    statut = contexte["pipeline"].get("status")
    assert statut == "success", message(
        en=(
            f"The latest pipeline on the default branch is '{statut}', not "
            "'success'. It was green before your changes: adding a cache and a "
            "report must not break it."
        ),
        fr=(
            f"Le dernier pipeline de la branche par défaut est « {statut} », "
            "pas « success ». Il était vert avant vos modifications : ajouter "
            "un cache et un rapport ne doit pas le casser."
        ),
    )
    rapport = api(
        forge,
        f"/projects/{contexte['projet']['id']}/pipelines/{contexte['pipeline']['id']}/test_report",
    )
    assert isinstance(rapport, dict), message(
        en="GitLab's test report for this pipeline could not be read.",
        fr="Le rapport de tests de ce pipeline n'a pas pu être lu.",
    )
    total = rapport.get("total_count") or 0
    assert total > 0, message(
        en=(
            "GitLab's test report is empty for this pipeline. An artifact "
            "declared with `paths:` alone is downloadable but never read: only "
            "`reports: junit:` fills the Tests tab."
        ),
        fr=(
            "Le rapport de tests de ce pipeline est vide. Un artefact déclaré "
            "avec `paths:` seul est téléchargeable mais jamais lu : seul "
            "`reports: junit:` remplit l'onglet Tests."
        ),
    )
    assert (rapport.get("failed_count") or 0) == 0, message(
        en=f"GitLab's test report lists {rapport.get('failed_count')} failed test(s).",
        fr=f"Le rapport de tests de GitLab compte {rapport.get('failed_count')} test(s) en échec.",
    )


def test_un_cache_a_ete_cree(traces_du_dernier):
    """Un cache declare se cree a la fin du job qui le porte.

    GitLab Runner ecrit « Creating cache … » ou « Saving cache … » selon la
    version : les deux formulations sont acceptees, parce que noter une version
    de runner n'est pas le sujet du lab.
    """
    motifs = ("creating cache", "saving cache")
    assert any(m in traces_du_dernier for m in motifs), message(
        en=(
            "No job log mentions creating a cache. Without `cache:`, every job "
            "downloads its dependencies again from scratch."
        ),
        fr=(
            "Aucun journal ne mentionne la création d'un cache. Sans `cache:`, "
            "chaque job retélécharge ses dépendances depuis zéro."
        ),
    )


def test_le_cache_a_servi_au_moins_une_fois(traces_du_dernier):
    """LA PREUVE QUE LE CACHE SERT, et c'est le coeur du lab.

    Un cache se cree au premier passage et ne se restaure qu'au suivant. Un
    test qui se contenterait de « Creating cache » noterait une intention : il
    passerait sur un pipeline unique, cache jamais relu. On exige donc une
    RESTAURATION, ce qui suppose un second passage du pipeline.
    """
    # UN SEUL MOTIF EST PROPRE AU SUCCES, et c'est une correction du
    # 2026-10-22. GitLab Runner ecrit « Restoring cache » puis « Checking cache
    # for <cle> » AVANT de savoir si le cache existe : les deux apparaissent
    # donc aussi quand il est absent, suivies d'un avertissement. Les accepter
    # rendait ce test complaisant.
    #
    # Ce lab y echappait parce que son etat de depart n'a aucun cache declare,
    # donc aucune de ces lignes ; le lab 12, lui, part d'un cache declare mais
    # introuvable, et le test y passait avant tout travail. Le motif se
    # resserre donc dans les deux, par principe.
    assert "successfully extracted cache" in traces_du_dernier, message(
        en=(
            "No job log shows a cache being restored. A cache is created on the "
            "first run and only restored on the next one: run the pipeline a "
            "second time and compare."
        ),
        fr=(
            "Aucun journal ne montre un cache restauré. Un cache se crée au "
            "premier passage et ne se restaure qu'au suivant : relancez le "
            "pipeline une seconde fois et comparez."
        ),
    )
