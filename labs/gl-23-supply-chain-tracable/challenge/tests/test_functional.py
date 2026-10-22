"""Tests du lab gl-23-supply-chain-tracable.

CE LAB NOTE CE QUE LA FORGE ET LE REGISTRE ONT VU, JAMAIS CE QUI EST ECRIT. Un
`.gitlab-ci.yml` qui declare un job `cosign sign` ne prouve rien : le job peut
ne jamais tourner, signer une autre image, ou echouer sans rien laisser. Les
tests lisent donc l'API de la forge (jobs, statuts, artefacts, journaux), et
pour les deux preuves qui comptent le plus, la signature et l'attestation, ils
INTERROGENT LE REGISTRE EUX-MEMES avec cosign, plutot que de croire le journal
d'un job. Une signature faite avec une autre cle, ou sur un autre digest,
passerait un test qui lirait le journal ; elle ne passe pas cosign verify.

LA REGLE QUI A COUTE QUATRE REECRITURES ailleurs vaut ici : l'etat de depart
publie son image sans SBOM, sans signature, sans attestation et sans
verification. Chacun des cinq tests porte sur une de ces absences, et aucun ne
peut etre vert au depart. Le setup MESURE ces absences avant de rendre la main.

CE QUE LES TESTS NE FONT PAS. Ils n'imposent ni le nom d'un job, ni sa place
exacte, ni le nom du fichier de SBOM, ni le nom de la variable qui designe
l'image a verifier. Ils reconnaissent un SBOM a son CONTENU (`bomFormat` vaut
`CycloneDX`), une signature a ce que cosign en dit, un refus a ce que le
journal du job contient. Ils ne jugent pas la qualite de la provenance, seulement
qu'elle est signee et qu'elle nomme le commit.

FAITS MESURES SUR CETTE INSTANCE QUE LES MESSAGES RESPECTENT :
  - un pipeline dont un job manuel attend porte le statut `manual`, pas
    `success` : un pipeline sain de ce projet finit `manual` ;
  - un job range dans une etape que `stages:` ne declare pas fait refuser TOUTE
    la configuration : pipeline `failed`, ZERO job, `yaml_errors` a `null`. Le
    linter CI du projet est alors le seul a nommer la cause ;
  - le projet est designe par son chemin exact, jamais par une recherche : un
    projet supprime reste 30 jours en retention (`gitlab.projet`).

FAITS NON MESURES PAR L'AUTEUR DE CE FICHIER, a rejouer sur l'instance :
  - les options de cosign (`--allow-insecure-registry`, `--insecure-ignore-tlog`)
    et le texte `no signatures found` viennent de la lecon
    `securite/supply-chain.mdx` (cosign 3.1.3), pas d'un essai ici. Le setup
    les exerce avant de rendre la main : s'ils sont faux, c'est lui qui echoue ;
  - le format de sortie de `cosign verify-attestation` (une enveloppe JSON par
    ligne, avec un champ `payload` en base64) vient de la meme lecon.
"""

from __future__ import annotations

import base64
import json
import re
import shlex
import sys
from datetime import datetime
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
    lint_configuration,
    pipelines,
    projet,
)

from conftest import lab_host, message  # noqa: E402

NOTE = "/opt/dsoxlab/gl-23/NOTE-SUPPLY-CHAIN.txt"
# Poses par le setup, hors du depot : la cle publique, et le script qui lance
# cosign avec l'authentification du registre (jeton lu sur la VM, jamais en
# argument).
CLES = "/var/lib/dsoxlab/gl-23-cles"
COSIGN = f"{CLES}/cosign-registre.sh"
PUB = f"{CLES}/cosign.pub"
REGISTRE = "gitlab-1.lab:5050"
IMAGE = f"{REGISTRE}/root/pipeline-craft"
# Registre en HTTP, journal de transparence public exclu : la lecon signe avec
# une configuration vide, donc la verification doit dire qu'aucun journal n'est
# attendu.
OPTIONS = ["--key", PUB, "--insecure-ignore-tlog=true", "--allow-insecure-registry"]

# Combien de pipelines de `main` on relit : l'etat de depart en porte un ou
# deux, un apprenant applique en ajoute quelques-uns (le pipeline de la
# signature, celui du refus, celui de la fin).
PIPELINES_RELUS = 6

# Ce qui rend un echec de verification NON PROBANT : cosign a echoue pour une
# raison de reseau, d'authentification ou d'option, pas faute de signature.
ERREURS_DE_REGISTRE = re.compile(
    r"UNAUTHORIZED|DENIED|server gave HTTP response|no such host|"
    r"connection refused|MANIFEST_UNKNOWN|NAME_UNKNOWN|x509|unknown flag",
    re.IGNORECASE,
)
SANS_SIGNATURE = re.compile(r"no (matching )?signatures", re.IGNORECASE)

# Script execute SUR LA VM : il telecharge l'archive d'artefacts d'un job et
# en extrait, de chaque fichier JSON qui est un SBOM CycloneDX, les noms de
# composants. Le SBOM entier peut peser plusieurs centaines de Ko : on ne
# rapatrie que ce que les tests lisent. Le jeton est lu dans le fichier de la
# VM, il ne figure dans aucune ligne de commande.
EXTRAIRE = r"""
import io, json, sys, urllib.request, zipfile
sortie = {"sboms": [], "erreur": None}
try:
    jeton = open("/etc/dsoxlab/jeton-api").read().strip()
    req = urllib.request.Request(sys.argv[1], headers={"PRIVATE-TOKEN": jeton})
    with urllib.request.urlopen(req, timeout=60) as r:
        donnees = r.read()
    with zipfile.ZipFile(io.BytesIO(donnees)) as z:
        for nom in z.namelist():
            if not nom.lower().endswith(".json"):
                continue
            brut = z.read(nom)
            try:
                doc = json.loads(brut)
            except ValueError:
                continue
            if not isinstance(doc, dict) or doc.get("bomFormat") != "CycloneDX":
                continue
            noms = [c.get("name") for c in doc.get("components") or [] if c.get("name")]
            sortie["sboms"].append({
                "fichier": nom,
                "version": doc.get("specVersion"),
                "composants": noms,
                "vise_le_projet": "root/pipeline-craft" in brut.decode("utf-8", "replace"),
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
def tiers(forge):
    """L'image que personne n'a signée, telle que le setup l'a consignée.

    Une note absente est une panne du lab, pas un échec de l'apprenant : le
    message le dit, au lieu de laisser croire que la vérification est mal écrite.
    """
    r = forge.run(f"cat {NOTE}")
    ref = re.search(r"^IMAGE-TIERS:\s*(\S+)", r.stdout, re.MULTILINE) if r.rc == 0 else None
    dig = re.search(r"^DIGEST-TIERS:\s*(sha256:[0-9a-f]{64})", r.stdout, re.MULTILINE) if r.rc == 0 else None
    assert ref and dig, message(
        en=(
            f"The setup note {NOTE} is missing or unreadable. The lab setup did "
            "not complete: replay it with dsoxlab run."
        ),
        fr=(
            f"La note du setup {NOTE} est absente ou illisible. Le setup du lab "
            "n'est pas allé au bout : rejouez-le avec dsoxlab run."
        ),
    )
    return {"ref": ref.group(1), "digest": dig.group(1)}


@pytest.fixture(scope="module")
def historique(forge, projet_du_lab):
    """Les derniers pipelines de `main`, du plus récent au plus ancien, avec leurs jobs."""
    return [
        {"pipeline": p, "jobs": jobs(forge, p["id"], projet_du_lab["id"])}
        for p in pipelines(forge, ref="main", projet_id=projet_du_lab["id"])[:PIPELINES_RELUS]
    ]


def _trace(host, projet_id: int, job_id: int) -> str:
    """Le journal d'un job, en texte brut ('' si la forge ne le rend pas)."""
    out = api(host, f"/projects/{projet_id}/jobs/{job_id}/trace", brut=True)
    return out if isinstance(out, str) else ""


def _cosign(host, *args: str):
    """Lance cosign sur la VM, authentifié sur le registre du lab."""
    return host.run(COSIGN + " " + " ".join(shlex.quote(a) for a in args))


def _digest_du_tag(host, projet_id: int, tag: str) -> str | None:
    """Le digest que le registre associe aujourd'hui à un tag du projet."""
    depots = api(host, f"/projects/{projet_id}/registry/repositories")
    for depot in depots if isinstance(depots, list) else []:
        t = api(host, f"/projects/{projet_id}/registry/repositories/{depot['id']}/tags/{tag}")
        if isinstance(t, dict) and t.get("digest"):
            return t["digest"]
    return None


def _pipeline_sain(historique: list) -> dict | None:
    """Le pipeline le plus récent qui a fini sain : `success`, ou `manual`.

    Un pipeline sain de ce projet finit `manual` (le déploiement de production
    attend une main). Le pipeline qui prouve le refus finit `failed` : il ne
    peut pas servir de pipeline « sain », et l'apprenant qui le laisse en
    dernier ne doit pas être noté sur lui.
    """
    for entree in historique:
        if entree["pipeline"].get("status") in ("success", "manual"):
            return entree
    return None


def _exiger_un_pipeline_sain(forge, projet_du_lab, historique) -> dict:
    assert historique, message(
        en="No pipeline on main: push your configuration.",
        fr="Aucun pipeline sur main : poussez votre configuration.",
    )
    dernier = historique[0]
    statut = dernier["pipeline"].get("status")
    assert statut not in ("created", "pending", "running", "waiting_for_resource"), message(
        en=(
            f"The latest pipeline is still {statut}. Wait for it to finish, then "
            "run the check again: the registry holds nothing final before that."
        ),
        fr=(
            f"Le dernier pipeline est encore {statut}. Attendez qu'il se termine, "
            "puis relancez la vérification : le registre ne contient rien de "
            "définitif avant."
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
    sain = _pipeline_sain(historique)
    assert sain is not None, message(
        en=(
            "No recent pipeline of main ended healthy (success, or manual while "
            "the production deployment waits). The last ones are: "
            + ", ".join(f"{e['pipeline']['id']}={e['pipeline'].get('status')}" for e in historique)
            + ". Fix the failing job, then push, or run a normal pipeline on main."
        ),
        fr=(
            "Aucun pipeline récent de main ne s'est terminé sain (success, ou "
            "manual tant que le déploiement de production attend). Les derniers "
            "sont : "
            + ", ".join(f"{e['pipeline']['id']}={e['pipeline'].get('status')}" for e in historique)
            + ". Corrigez le job en échec, puis poussez, ou lancez un pipeline "
            "normal sur main."
        ),
    )
    return sain


def _sboms_du_job(host, projet_id: int, job_id: int) -> list[dict]:
    """Les SBOM CycloneDX contenus dans l'archive d'artefacts d'un job."""
    url = f"{URL}/api/v4/projects/{projet_id}/jobs/{job_id}/artifacts"
    r = host.run(f"python3 -c {shlex.quote(EXTRAIRE)} {shlex.quote(url)}")
    if r.rc != 0 or not r.stdout.strip():
        return []
    try:
        return json.loads(r.stdout).get("sboms") or []
    except json.JSONDecodeError:
        return []


def _normaliser(nom: str) -> str:
    return nom.lower().replace("_", "-")


def test_un_sbom_cyclonedx_de_l_image_est_publie_en_artefact(forge, projet_du_lab, historique):
    """LE SBOM EXISTE DANS LA FORGE, au format CycloneDX, et décrit CETTE image.

    Le pipeline de départ publie l'image et n'en dresse aucun inventaire : aucun
    artefact JSON ne porte `bomFormat: CycloneDX`. Ce test ne peut donc pas
    être vert avant que l'apprenant ait écrit son job.

    Trois exigences, parce qu'un SBOM vide ou étranger est pire qu'absent (il
    est signé puis cru) :

      1. un job réussi a laissé, dans ses artefacts, un document CycloneDX
         (reconnu à son contenu, pas à un nom de fichier ou de job) ;
      2. il décrit l'image de ce projet (le nom `root/pipeline-craft` y figure) ;
      3. il liste des composants, dont au moins un paquet de `requirements.txt`
         : l'inventaire d'une autre image, ou d'une image vide, n'en contient
         pas. La leçon dit qu'un SBOM se contrôle avant d'être signé.

    Le test lit le dernier pipeline SAIN, pas le dernier tout court : un
    apprenant qui laisse en dernier le pipeline du refus (volontairement en
    échec) ne doit pas perdre son SBOM.
    """
    sain = _exiger_un_pipeline_sain(forge, projet_du_lab, historique)
    sboms = []
    for j in sain["jobs"]:
        archive = j.get("artifacts_file") or any(
            a.get("file_type") == "archive" for a in (j.get("artifacts") or [])
        )
        if j.get("status") == "success" and archive:
            sboms += _sboms_du_job(forge, projet_du_lab["id"], j["id"])
    assert sboms, message(
        en=(
            "No successful job of the latest healthy pipeline kept a CycloneDX "
            "SBOM in its artifacts. Either no job inventories the image, or the "
            "output is not CycloneDX (Syft: `-o cyclonedx-json=<file>`), or the "
            "job does not publish it (`artifacts: paths:`)."
        ),
        fr=(
            "Aucun job réussi du dernier pipeline sain n'a laissé de SBOM "
            "CycloneDX dans ses artefacts. Soit aucun job n'inventorie l'image, "
            "soit la sortie n'est pas du CycloneDX (Syft : "
            "`-o cyclonedx-json=<fichier>`), soit le job ne la publie pas "
            "(`artifacts: paths:`)."
        ),
    )
    visant = [s for s in sboms if s["vise_le_projet"]]
    assert visant, message(
        en=(
            "The SBOM does not mention root/pipeline-craft: it describes another "
            "image. Syft must read the image this pipeline published, "
            "`registry:$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA`."
        ),
        fr=(
            "Le SBOM ne mentionne pas root/pipeline-craft : il décrit une autre "
            "image. Syft doit lire l'image que ce pipeline a publiée, "
            "`registry:$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA`."
        ),
    )
    requis = fichier(forge, "requirements.txt", "main", projet_du_lab["id"]) or ""
    paquets = {
        _normaliser(m.group(1))
        for ligne in requis.splitlines()
        if (m := re.match(r"\s*([A-Za-z0-9_.\-]+)", ligne))
    }
    for s in visant:
        presents = {_normaliser(n) for n in s["composants"]}
        if len(presents) >= 10 and (presents & paquets):
            return
    pytest.fail(
        message(
            en=(
                "The SBOM is empty or incomplete: "
                + ", ".join(f"{len(s['composants'])} components" for s in visant)
                + f". An inventory of this image lists its OS packages and at "
                f"least one of the application dependencies ({sorted(paquets)})."
            ),
            fr=(
                "Le SBOM est vide ou incomplet : "
                + ", ".join(f"{len(s['composants'])} composants" for s in visant)
                + ". L'inventaire de cette image liste ses paquets système et au "
                f"moins une des dépendances de l'application ({sorted(paquets)})."
            ),
        )
    )


def test_l_image_du_commit_est_signee_et_la_cle_privee_n_a_pas_fuite(
    forge, projet_du_lab, historique
):
    """LA SIGNATURE EST DANS LE REGISTRE, vérifiable avec la clé publique du projet.

    Le pipeline de départ publie l'image et ne la signe pas : `cosign verify`
    répond `no signatures found`. Ce test ne peut donc pas être vert au départ.

    POURQUOI VERIFIER LE REGISTRE ET PAS LE JOURNAL. Un job `cosign sign` peut
    réussir sur un autre digest que celui que le registre sert, ou avec une
    autre clé : le journal est vert, la signature ne vaut rien. Le test lance
    donc cosign lui-même, sur le DIGEST que le registre associe aujourd'hui au
    tag du commit, avec la clé publique posée par le setup. Un digest, et non
    un tag : une signature se pose sur un contenu, pas sur une étiquette qu'un
    autre push peut déplacer.

    Il y joint deux exigences vraies au départ, qui ne valent pas un test à
    elles seules : la clé privée n'est dans aucun fichier du dépôt, et aucun
    journal du pipeline ne la montre. Signer avec une clé qu'on a commitée ou
    affichée, c'est signer avec une clé que tout le monde a.
    """
    sain = _exiger_un_pipeline_sain(forge, projet_du_lab, historique)
    pid = projet_du_lab["id"]
    court = str(sain["pipeline"]["sha"])[:8]
    digest = _digest_du_tag(forge, pid, court)
    assert digest, message(
        en=(
            f"The registry holds no image tagged {court}: the build job did not "
            "publish it, or it was deleted."
        ),
        fr=(
            f"Le registre ne contient aucune image taguée {court} : le job de "
            "construction ne l'a pas publiée, ou elle a été supprimée."
        ),
    )
    r = _cosign(forge, "verify", *OPTIONS, f"{IMAGE}@{digest}")
    queue = (r.stderr or r.stdout or "").strip().splitlines()[-4:]
    assert r.rc == 0, message(
        en=(
            f"cosign verify refuses {IMAGE}@{digest[:19]}... with the project's "
            "public key (cosign.pub). Last lines: "
            + " | ".join(queue)
            + ". 'no signatures found' means nothing signed this digest: sign "
            "the image, by digest, with the COSIGN_PRIVATE_KEY variable of the "
            "project."
        ),
        fr=(
            f"cosign verify refuse {IMAGE}@{digest[:19]}... avec la clé "
            "publique du projet (cosign.pub). Dernières lignes : "
            + " | ".join(queue)
            + ". « no signatures found » veut dire que rien n'a signé ce "
            "digest : signez l'image, par digest, avec la variable "
            "COSIGN_PRIVATE_KEY du projet."
        ),
    )
    arbre = api(forge, f"/projects/{pid}/repository/tree", "recursive=true&per_page=100&ref=main")
    chemins = [e.get("path", "") for e in arbre] if isinstance(arbre, list) else []
    cles_commitees = [c for c in chemins if c.rsplit("/", 1)[-1] == "cosign.key"]
    assert not cles_commitees, message(
        en=f"The private key is in the repository: {cles_commitees}. Remove it and treat the key as leaked.",
        fr=f"La clé privée est dans le dépôt : {cles_commitees}. Retirez-la et considérez la clé comme compromise.",
    )
    fuites = [
        j["name"]
        for j in sain["jobs"]
        if "ENCRYPTED SIGSTORE PRIVATE KEY" in _trace(forge, pid, j["id"])
    ]
    assert not fuites, message(
        en=f"The private key appears in the log of: {fuites}. Never print it; treat the key as leaked.",
        fr=f"La clé privée apparaît dans le journal de : {fuites}. Ne l'affichez jamais ; considérez la clé comme compromise.",
    )


def test_la_provenance_est_attestee_et_nomme_le_commit(forge, projet_du_lab, historique):
    """L'ATTESTATION DE PROVENANCE EST DANS LE REGISTRE, signée, et nomme le commit.

    Le pipeline de départ n'atteste rien : `cosign verify-attestation` ne
    trouve aucune attestation. Ce test ne peut donc pas être vert au départ.

    Une signature prouve que l'image n'a pas changé ; elle ne dit pas d'où elle
    vient. L'attestation de provenance lie l'image au build qui l'a produite.
    Le test exige donc que l'attestation (type `slsaprovenance`, celui de la
    leçon) se vérifie avec la clé du projet, et que son contenu nomme le SHA du
    commit du pipeline : une provenance qui ne dit pas quel commit a été
    construit ne prouve rien de l'origine.

    Comme pour la signature, c'est cosign qui tranche sur le registre, pas le
    journal d'un job. Il ne juge pas le reste du prédicat.
    """
    sain = _exiger_un_pipeline_sain(forge, projet_du_lab, historique)
    sha = str(sain["pipeline"]["sha"])
    digest = _digest_du_tag(forge, projet_du_lab["id"], sha[:8])
    assert digest, message(
        en=f"The registry holds no image tagged {sha[:8]}.",
        fr=f"Le registre ne contient aucune image taguée {sha[:8]}.",
    )
    r = _cosign(
        forge, "verify-attestation", *OPTIONS, "--type", "slsaprovenance", f"{IMAGE}@{digest}"
    )
    queue = (r.stderr or "").strip().splitlines()[-4:]
    assert r.rc == 0, message(
        en=(
            "No provenance attestation (type slsaprovenance) verifies against "
            "the project's public key on this image. Last lines: "
            + " | ".join(queue)
            + ". Attach the provenance with `cosign attest --type "
            "slsaprovenance --predicate <file>`, signed with the same key as the image."
        ),
        fr=(
            "Aucune attestation de provenance (type slsaprovenance) ne se "
            "vérifie avec la clé publique du projet sur cette image. Dernières "
            "lignes : "
            + " | ".join(queue)
            + ". Attachez la provenance avec `cosign attest --type "
            "slsaprovenance --predicate <fichier>`, signée avec la même clé que l'image."
        ),
    )
    textes = []
    for ligne in (r.stdout or "").splitlines():
        if not ligne.startswith("{"):
            continue
        textes.append(ligne)
        try:
            charge = json.loads(ligne).get("payload", "")
            textes.append(base64.b64decode(charge).decode("utf-8", "replace"))
        except (ValueError, AttributeError):
            continue
    assert any(sha in t for t in textes), message(
        en=(
            f"The attestation verifies, but its content does not name the commit "
            f"{sha}. A provenance says what was built, from which source: put "
            "$CI_COMMIT_SHA in the predicate."
        ),
        fr=(
            f"L'attestation se vérifie, mais son contenu ne nomme pas le commit "
            f"{sha}. Une provenance dit ce qui a été construit, à partir de quelle "
            "source : mettez $CI_COMMIT_SHA dans le prédicat."
        ),
    )


def test_une_image_non_signee_a_ete_refusee_avant_tout_deploiement(
    forge, projet_du_lab, historique, tiers
):
    """LE REFUS EST REEL : un job de vérification a échoué, faute de signature.

    Signer sans vérifier ne protège de rien, et un job de vérification qui n'a
    jamais échoué n'a jamais prouvé qu'il savait le faire. Le setup a posé dans
    le registre une image `tiers` que personne n'a signée. Ce test cherche,
    dans les derniers pipelines de `main`, un pipeline qui prouve les cinq
    faits du refus :

      1. un job a ÉCHOUÉ en `script_failure` (le script a rendu un code
         d'erreur : ce n'est ni un runner absent, ni un délai) ;
      2. il n'est pas `allow_failure`, sinon son échec ne bloquerait rien ;
      3. son journal NOMME l'image tiers (tag ou digest) : c'est cette image
         qu'il a refusée, pas celle du commit ;
      4. son journal porte la CAUSE donnée par cosign, « no signatures found »,
         et aucun signe d'un registre injoignable, d'un refus d'authentification
         ou d'une option inconnue : ces échecs-là ressemblent à une absence de
         signature et ne prouvent rien (la lecon montre un script qui jette la
         sortie d'erreur de cosign avec `2>/dev/null` ; il faut la garder) ;
      5. aucun job de l'étape `deploy` n'a agi : le refus est arrivé AVANT.

    Un pipeline sain de ce projet finit `manual` ; le pipeline du refus finit
    `failed`, et c'est ce qui le distingue. Le test cherche dans l'historique
    et non dans le dernier pipeline seul : l'apprenant relance ensuite un
    pipeline normal, et le refus doit rester lisible.
    """
    assert historique, message(
        en="No pipeline on main: push your configuration.",
        fr="Aucun pipeline sur main : poussez votre configuration.",
    )
    pid = projet_du_lab["id"]
    hex_tiers = tiers["digest"].split(":", 1)[1]
    preuves = []
    bilan = []
    for entree in historique:
        pipeline = entree["pipeline"]
        if pipeline.get("status") != "failed":
            continue
        ont_agi = [
            x["name"]
            for x in entree["jobs"]
            if x.get("stage") == "deploy"
            and x.get("status") in ("success", "running", "pending", "manual", "failed")
        ]
        for j in entree["jobs"]:
            if j.get("status") != "failed" or j.get("allow_failure"):
                continue
            if j.get("failure_reason") != "script_failure":
                continue
            trace = _trace(forge, pid, j["id"])
            vise_tiers = "pipeline-craft:tiers" in trace or hex_tiers in trace
            cause = bool(SANS_SIGNATURE.search(trace))
            panne = ERREURS_DE_REGISTRE.search(trace)
            bilan.append(
                f"pipeline {pipeline['id']}, job {j['name']}: "
                f"image tiers nommée={vise_tiers}, cause 'no signatures'={cause}, "
                f"panne de registre={panne.group(0) if panne else None}, "
                f"déploiements actifs={ont_agi}"
            )
            if vise_tiers and cause and not panne and not ont_agi:
                preuves.append(pipeline["id"])
    assert preuves, message(
        en=(
            "No pipeline shows a real refusal. Expected: a job failed with "
            "script_failure, not allow_failure, whose log names the `tiers` image "
            "and keeps cosign's reason ('no signatures found'), with no deploy "
            "job having run. Seen: "
            + ("; ".join(bilan) if bilan else "no failed job in the recent pipelines of main")
            + ". Make the verification target the `tiers` image (it must be "
            "able to target another image than the commit's), keep cosign's "
            "error output in the log, and place the job before the deploy stage."
        ),
        fr=(
            "Aucun pipeline ne montre un vrai refus. On attend : un job en "
            "échec (script_failure), qui n'est pas allow_failure, dont le "
            "journal nomme l'image `tiers` et garde la raison de cosign "
            "(« no signatures found »), sans qu'aucun job de déploiement ait "
            "agi. Constaté : "
            + ("; ".join(bilan) if bilan else "aucun job en échec dans les derniers pipelines de main")
            + ". Faites porter la vérification sur l'image `tiers` (elle doit "
            "pouvoir viser une autre image que celle du commit), gardez la "
            "sortie d'erreur de cosign dans le journal, et placez le job avant "
            "l'étape de déploiement."
        ),
    )


def _horodatage(valeur: str | None) -> datetime | None:
    if not valeur:
        return None
    try:
        return datetime.fromisoformat(valeur.replace("Z", "+00:00"))
    except ValueError:
        return None


def test_la_verification_est_dans_la_chaine_et_passe_avant_le_deploiement(
    forge, projet_du_lab, historique
):
    """LA VÉRIFICATION FAIT PARTIE DE LA CHAÎNE QUI LIVRE, et elle passe avant.

    Le pipeline de départ n'a aucun job qui vérifie quoi que ce soit : aucun
    journal ne contient `cosign verify`. Ce test ne peut donc pas être vert au
    départ.

    Le refus du test précédent prouve que la vérification SAIT échouer. Celui-ci
    prouve qu'elle est installée dans la chaîne normale : dans le dernier
    pipeline sain, un job réussi, non `allow_failure`, a lancé `cosign verify`,
    et il a FINI avant que le premier job de déploiement ne COMMENCE. Une
    vérification placée après le déploiement constate l'incident, elle ne
    l'empêche pas.

    Le test ne reconnaît pas le job à son nom mais à sa commande, telle que
    GitLab l'écrit dans le journal (`$ cosign verify ...`). `cosign
    verify-attestation` ne compte pas : il contrôle l'attestation, pas l'image.
    """
    sain = _exiger_un_pipeline_sain(forge, projet_du_lab, historique)
    pid = projet_du_lab["id"]
    candidats = [
        j
        for j in sain["jobs"]
        if j.get("status") == "success"
        and not j.get("allow_failure")
        and re.search(r"cosign\s+verify(?!-)", _trace(forge, pid, j["id"]))
    ]
    assert candidats, message(
        en=(
            "No successful job of the latest healthy pipeline ran `cosign "
            "verify`. The pipeline signs but never checks: add a job that "
            "verifies the signature and cannot fail silently (not "
            "`allow_failure`)."
        ),
        fr=(
            "Aucun job réussi du dernier pipeline sain n'a lancé `cosign "
            "verify`. Le pipeline signe mais ne vérifie jamais : ajoutez un job "
            "qui vérifie la signature et ne peut pas échouer en silence (pas "
            "de `allow_failure`)."
        ),
    )
    departs = [
        (_horodatage(j.get("started_at")), j["name"])
        for j in sain["jobs"]
        if j.get("stage") == "deploy" and j.get("started_at")
    ]
    departs = [(t, n) for t, n in departs if t is not None]
    assert departs, message(
        en=(
            "No deploy job started in the latest healthy pipeline: nothing to "
            "compare the verification with. Keep the deploy stage of the project."
        ),
        fr=(
            "Aucun job de déploiement n'a démarré dans le dernier pipeline sain : "
            "rien à comparer avec la vérification. Gardez l'étape de déploiement "
            "du projet."
        ),
    )
    premier, nom_deploiement = min(departs)
    en_retard = [
        j["name"]
        for j in candidats
        if (_horodatage(j.get("finished_at")) or premier) > premier
    ]
    assert len(en_retard) < len(candidats), message(
        en=(
            f"The verification ({', '.join(en_retard)}) finishes after the first "
            f"deployment started ({nom_deploiement}). Verifying after deploying "
            "reports the incident instead of preventing it: move the job to a "
            "stage before `deploy`."
        ),
        fr=(
            f"La vérification ({', '.join(en_retard)}) se termine après le début "
            f"du premier déploiement ({nom_deploiement}). Vérifier après avoir "
            "déployé constate l'incident au lieu de l'empêcher : placez le job "
            "dans une étape avant `deploy`."
        ),
    )
