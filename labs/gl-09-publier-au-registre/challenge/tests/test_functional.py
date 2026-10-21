"""Tests du lab gl-09-publier-au-registre.

CE QUE CE LAB MESURE : qu'une image construite par le pipeline est devenue
RECUPERABLE, et qu'on peut dire de quel commit elle vient.

UN ARBITRAGE EST EN ATTENTE, ET CES TESTS NE LE TRANCHENT PAS. La page du site
enseigne de publier deux tags, celui du commit et `latest`, alors que la regle
du depot interdit `:latest`, meme dans un extrait illustratif. Le constat est
consigne dans `todo/defauts-fr-gitlab-remontes.md` cote site, et la decision
appartient a Stephane.

Ces tests exigent donc le TAG IMMUABLE, qui n'est contesté par personne et qui
est la vraie competence : une image dont le nom designe un commit precis. Un
tag `latest` est ACCEPTE s'il est la, et jamais exige. Un apprenant qui suit la
page reussit, un apprenant qui suit la regle du depot reussit aussi.

LE TEST QUI COMPTE VRAIMENT est le second : le tag publie doit correspondre au
SHA COURT DU DERNIER COMMIT. C'est ce qui distingue une image publiee d'une
image tracable. Une image poussee sous un nom quelconque ne se relie a aucun
code, et c'est precisement ce que la chaine d'approvisionnement reproche aux
references mobiles.
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
def projet_du_lab(forge):
    p = projet(forge)
    assert p is not None, message(
        en="The pipeline-craft project was not found on the lab GitLab instance.",
        fr="Le projet pipeline-craft n'a pas été trouvé sur le GitLab du lab.",
    )
    return p


@pytest.fixture(scope="module")
def images(forge, projet_du_lab):
    """Les tags publies dans le registre du projet, tous depots confondus."""
    trouves: list[str] = []
    depots = api(forge, f"/projects/{projet_du_lab['id']}/registry/repositories")
    if isinstance(depots, list):
        for d in depots:
            tags = api(
                forge,
                f"/projects/{projet_du_lab['id']}/registry/repositories/{d['id']}/tags",
            )
            if isinstance(tags, list):
                trouves += [t.get("name") for t in tags if t.get("name")]
    return trouves


def test_une_image_est_publiee_dans_le_registre(images):
    assert images, message(
        en=(
            "The project's container registry is empty. An image built and "
            "never pushed lives as long as its job, then disappears with it: "
            "nobody can deploy it."
        ),
        fr=(
            "Le registre de conteneurs du projet est vide. Une image construite "
            "et jamais poussée vit le temps de son job, puis disparaît avec "
            "lui : personne ne peut la déployer."
        ),
    )


def test_un_tag_designe_le_commit_publie(forge, projet_du_lab, images):
    """LE TEST QUI COMPTE : l'image publiee se relie-t-elle a un commit ?

    Une image poussee sous un nom quelconque ne designe aucun code. Le tag doit
    porter le SHA court du dernier commit de la branche par defaut, ce que
    `$CI_COMMIT_SHORT_SHA` fournit au pipeline.

    On accepte un prefixe ou un suffixe autour du SHA : `sha-1a2b3c4d` ou
    `1a2b3c4d` conviennent tous deux. Ce qui est refuse, c'est qu'AUCUN tag ne
    porte le SHA.
    """
    branche = projet_du_lab.get("default_branch") or "main"
    commits = api(
        forge,
        f"/projects/{projet_du_lab['id']}/repository/commits",
        f"ref_name={branche}&per_page=1",
    )
    assert isinstance(commits, list) and commits, message(
        en="The default branch's last commit could not be read.",
        fr="Le dernier commit de la branche par défaut n'a pas pu être lu.",
    )
    court = (commits[0].get("short_id") or "")[:8]
    assert court, message(
        en="The last commit has no short identifier.",
        fr="Le dernier commit n'a pas d'identifiant court.",
    )

    correspondants = [t for t in images if court in t]
    assert correspondants, message(
        en=(
            f"No published tag carries the last commit's short SHA ('{court}'). "
            f"Tags found: {images}. An image whose name designates no commit "
            "cannot be traced back to the code it runs."
        ),
        fr=(
            f"Aucun tag publié ne porte le SHA court du dernier commit "
            f"(« {court} »). Tags trouvés : {images}. Une image dont le nom ne "
            "désigne aucun commit ne se relie pas au code qu'elle exécute."
        ),
    )


def test_la_publication_a_reellement_eu_lieu_dans_un_job(forge, projet_du_lab):
    """La trace du job, et pas seulement le resultat.

    Le registre pourrait porter une image poussee a la main depuis la machine.
    Ce test verifie que c'est le PIPELINE qui a publie : un job reussi dont le
    journal porte une authentification suivie d'un envoi.
    """
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut.",
    )
    tous = jobs(forge, dernier["id"], projet_du_lab["id"])
    reussis = [j for j in tous if j.get("status") == "success"]

    publiants = []
    for j in reussis:
        brut = api(
            forge,
            f"/projects/{projet_du_lab['id']}/jobs/{j['id']}/trace",
            brut=True,
        )
        t = (brut or "").lower()
        if "docker push" in t or "pushed" in t or "digest:" in t:
            publiants.append(j.get("name"))

    assert publiants, message(
        en=(
            "No successful job's log shows an image being pushed. The registry "
            "may hold an image pushed by hand: the lab asks for the pipeline "
            "to publish it."
        ),
        fr=(
            "Aucun journal de job réussi ne montre un envoi d'image. Le "
            "registre peut porter une image poussée à la main : le lab demande "
            "que ce soit le pipeline qui publie."
        ),
    )

    # LA SANTE DU PIPELINE EST EXIGEE ICI, et pas dans un test a elle. Le
    # pipeline de depart de ce lab est sain : il construit l'image sans la
    # publier. Un test « aucun job n'a echoue » passerait donc AVANT tout
    # travail, ce que `valider-labs.py` refuse, et c'est la quatrieme fois que
    # ce motif se presente dans ce catalogue.
    #
    # A noter : le statut GLOBAL du pipeline est `manual` a ce rang du
    # parcours, le deploiement de production attendant sa decision. Exiger
    # `success` ferait echouer un travail juste.
    echoues = [
        j.get("name") for j in tous
        if j.get("status") in ("failed", "canceled")
    ]
    assert not echoues, message(
        en=(
            f"These jobs failed in the latest pipeline: {echoues} (pipeline "
            f"status '{dernier.get('status')}'). Publishing must not break what "
            "worked."
        ),
        fr=(
            f"Ces jobs ont échoué dans le dernier pipeline : {echoues} (statut "
            f"du pipeline « {dernier.get('status')} »). Publier ne doit pas "
            "casser ce qui marchait."
        ),
    )

