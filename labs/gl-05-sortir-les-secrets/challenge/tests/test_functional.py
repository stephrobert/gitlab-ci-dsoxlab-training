"""Tests du lab gl-05-sortir-les-secrets.

LE PIPELINE DE DEPART EST VERT, ET C'EST LE PROBLEME. Un secret en clair ne
casse rien : il fuit. Aucun test ne verifie donc ici que le pipeline est vert,
ce qui serait vrai avant tout travail et ne mesurerait que l'hypothese du
setup. Les trois tests portent sur ce que l'etat de depart ne porte pas.

CE QUE LE LAB MESURE, dans l'ordre des trois gestes :

- le secret a disparu DU DEPOT, aux deux endroits ou il se cache : la valeur de
  repli dans le code Python, et la variable du fichier de pipeline. On lit la
  forge, pas le disque : un fichier corrige mais non pousse ne protege rien ;
- une variable de CI existe, **masquee**, et sur une instance ou la branche par
  defaut est protegee, **protegee** aussi. C'est le remplacement du secret, pas
  seulement son retrait ;
- le secret n'apparait dans AUCUN journal de job du dernier pipeline. C'est la
  preuve qui compte : le masquage ne vaut que s'il tient a l'execution.

CE QU'ON NE FAIT JAMAIS ICI : lire la VALEUR d'une variable de CI. L'API la
rendrait, et un test qui l'affiche dans son message d'echec publierait le
secret dans la sortie de `dsoxlab check`. On ne lit que le nom et les
attributs.
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
    fichier,
    forge_joignable,
    jobs,
    projet,
)

from conftest import lab_host, message  # noqa: E402

# Le secret plante dans la branche de depart, a deux endroits. Il est ecrit ici
# parce que les tests doivent le CHERCHER : ce n'est pas un secret de
# production, c'est le leurre du lab.
LEURRE = "s3cret"


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


def test_le_secret_a_disparu_du_depot(forge, projet_du_lab):
    """Les deux cachettes du secret, lues dans la forge.

    `app/config.py` le portait en valeur de repli de `os.getenv`, et
    `.gitlab-ci.yml` en variable de pipeline. Les deux comptent : retirer l'une
    et garder l'autre laisse le secret dans l'historique ET dans le depot.
    """
    restants = []
    for chemin in ("app/config.py", ".gitlab-ci.yml"):
        contenu = fichier(forge, chemin, projet_id=projet_du_lab["id"])
        assert contenu is not None, message(
            en=f"{chemin} was not found in the repository on the default branch.",
            fr=f"{chemin} est introuvable dans le dépôt, sur la branche par défaut.",
        )
        if LEURRE in contenu:
            restants.append(chemin)
    assert not restants, message(
        en=(
            f"The hard-coded secret is still in the repository, in: {restants}. "
            "A secret committed once stays in the history: here, removing it "
            "from the default branch is what the lab asks."
        ),
        fr=(
            f"Le secret codé en dur est encore dans le dépôt, dans : "
            f"{restants}. Un secret commité une fois reste dans l'historique : "
            "ici, le lab demande de le retirer de la branche par défaut."
        ),
    )


def test_une_variable_de_ci_remplace_le_secret(forge, projet_du_lab):
    """Le secret doit avoir un remplacant, declare dans GitLab.

    On ne lit que le NOM et les ATTRIBUTS, jamais la valeur : un message
    d'echec qui la contiendrait publierait le secret dans la sortie du
    `dsoxlab check`.

    `protected` n'est exige que si la branche par defaut est elle-meme
    protegee : sur une instance ou elle ne l'est pas, une variable protegee ne
    serait jamais transmise au job, et l'exiger punirait un apprenant qui a
    bien travaille.
    """
    variables = api(forge, f"/projects/{projet_du_lab['id']}/variables", "per_page=100")
    assert isinstance(variables, list), message(
        en="The project's CI/CD variables could not be read.",
        fr="Les variables CI/CD du projet n'ont pas pu être lues.",
    )
    assert variables, message(
        en=(
            "The project has no CI/CD variable. Removing the secret is half "
            "the work: the value has to come from somewhere, declared under "
            "Settings > CI/CD > Variables."
        ),
        fr=(
            "Le projet n'a aucune variable CI/CD. Retirer le secret est la "
            "moitié du travail : la valeur doit venir de quelque part, "
            "déclarée dans Settings > CI/CD > Variables."
        ),
    )

    masquees = [v for v in variables if v.get("masked")]
    assert masquees, message(
        en=(
            f"None of the {len(variables)} CI/CD variable(s) is masked. "
            "Without masking, the value appears in plain text in any job log "
            "that echoes it."
        ),
        fr=(
            f"Aucune des {len(variables)} variable(s) CI/CD n'est masquée. "
            "Sans masquage, la valeur apparaît en clair dans tout journal de "
            "job qui l'affiche."
        ),
    )

    branches = api(forge, f"/projects/{projet_du_lab['id']}/protected_branches")
    defaut = projet_du_lab.get("default_branch") or "main"
    defaut_protegee = isinstance(branches, list) and any(
        b.get("name") == defaut for b in branches
    )
    if defaut_protegee:
        protegees = [v for v in masquees if v.get("protected")]
        assert protegees, message(
            en=(
                f"No masked variable is protected, while '{defaut}' is a "
                "protected branch. A protected variable is only handed to jobs "
                "on protected branches and tags: that is what keeps it out of "
                "a fork's pipeline."
            ),
            fr=(
                f"Aucune variable masquée n'est protégée, alors que « {defaut} » "
                "est une branche protégée. Une variable protégée n'est remise "
                "qu'aux jobs des branches et étiquettes protégées : c'est ce "
                "qui la tient hors du pipeline d'un fork."
            ),
        )


def test_le_secret_n_apparait_dans_aucun_journal(forge, projet_du_lab):
    """LA PREUVE QUI COMPTE : le masquage tient-il a l'execution ?

    Un secret retire du depot mais affiche par un `echo` reste lisible dans le
    journal, et un journal se telecharge. On lit donc tous les journaux du
    dernier pipeline.
    """
    dernier = dernier_pipeline(forge, projet_du_lab.get("default_branch") or "main")
    assert dernier is not None, message(
        en="No pipeline has run on the default branch since your changes.",
        fr="Aucun pipeline n'a tourné sur la branche par défaut depuis vos modifications.",
    )
    tous = jobs(forge, dernier["id"], projet_du_lab["id"])
    coupables = []
    for j in tous:
        brut = api(
            forge,
            f"/projects/{projet_du_lab['id']}/jobs/{j['id']}/trace",
            brut=True,
        )
        if brut and LEURRE in brut:
            coupables.append(j.get("name"))
    assert not coupables, message(
        en=(
            f"The secret is still readable in these jobs' logs: {coupables}. "
            "A log can be downloaded by anyone who can see the project."
        ),
        fr=(
            f"Le secret est encore lisible dans les journaux de ces jobs : "
            f"{coupables}. Un journal se télécharge, par quiconque voit le "
            "projet."
        ),
    )
