"""Acces a l'API GitLab depuis les tests d'un lab.

Tous les labs de ce catalogue notent l'ETAT LAISSE SUR LA FORGE, jamais les
commandes tapees : un apprenant qui atteint le bon etat par un autre chemin a
reussi. Or l'etat d'un pipeline ne se lit pas sur le disque, il se lit dans
l'API. Ce module est donc la porte d'entree unique, et il existe pour trois
raisons.

LA PREMIERE EST QU'UN `.gitlab-ci.yml` VALIDE NE PROUVE RIEN. Le fichier peut
etre parfait et le pipeline n'avoir jamais tourne, avoir echoue, ou avoir
tourne sur une autre branche. Lire le fichier reviendrait a noter l'intention ;
on note le resultat.

LA DEUXIEME EST QUE LE JETON NE DOIT PAS CIRCULER. Il est pose par le socle
dans `/etc/dsoxlab/jeton-api` sur la VM, et les appels partent DE la VM, pas du
poste. Il n'apparait donc ni dans une ligne de commande du poste, ni dans un
argument de test, ni dans la sortie d'un echec.

LA TROISIEME EST QU'UN APPEL QUI ECHOUE DOIT LE DIRE. Une API injoignable, un
jeton refuse ou un projet absent rendent `None` plutot qu'une exception
illisible, et les tests transforment ce `None` en message explicite. Un test
qui passe parce qu'il n'a rien pu mesurer serait le pire des resultats.
"""

from __future__ import annotations

import json
import shlex

# Hote de la forge, declare dans meta.yml sous infra.hosts.
HOTE = "gitlab-1.lab"
URL = "http://gitlab-1.lab"
# Le depot fil rouge, pousse par l'apprenant dans la forge du lab.
PROJET = "pipeline-craft"


def api(host, chemin: str, params: str = "", brut: bool = False) -> object | None:
    """Appelle l'API GitLab depuis la VM et rend le JSON, ou None.

    `chemin` commence par `/` et suit `/api/v4`. `params` est une chaine de
    requete deja encodee, sans le `?`.

    `brut=True` rend le TEXTE de la reponse au lieu de la decoder. Deux
    endpoints en ont besoin, et ce ne sont pas des cas marginaux : le journal
    d'un job (`/jobs/:id/trace`) et le contenu d'un fichier
    (`/repository/files/:chemin/raw`) ne rendent pas du JSON. Les decoder
    donnerait `None`, c'est-a-dire un test qui croit ne rien avoir trouve.
    """
    url = f"{URL}/api/v4{chemin}"
    if params:
        url += f"?{params}"
    # Le jeton est lu dans le fichier par le shell de la VM : il ne passe donc
    # jamais par la ligne de commande vue depuis le poste.
    cmd = (
        'JETON=$(cat /etc/dsoxlab/jeton-api 2>/dev/null); '
        '[ -n "$JETON" ] || exit 64; '
        f'curl -sS --max-time 20 -H "PRIVATE-TOKEN: $JETON" {shlex.quote(url)}'
    )
    r = host.run(cmd)
    if r.rc != 0 or not r.stdout.strip():
        return None
    if brut:
        return r.stdout
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def api_ecrire(
    host, methode: str, chemin: str, champs: dict[str, str] | None = None
) -> tuple[int, object | None]:
    """Ecrit dans l'API GitLab depuis la VM : POST, PUT ou DELETE.

    Rend le couple (code HTTP, corps decode). Le corps vaut None quand la
    reponse est vide, ce qui est normal sur un DELETE.

    POURQUOI UN TEST ECRIT PARFOIS. Certaines proprietes d'un pipeline ne se
    lisent nulle part : savoir si une branche de travail declenche un
    deploiement demande de pousser une branche et de regarder ce que la forge
    en fait. Les regles se combinent, le bloc `workflow:` peut en annuler une,
    et seule l'evaluation du serveur tranche.

    POURQUOI PAR L'API ET NON PAR GIT, mesure le 2026-10-22. La copie de
    travail de la VM vit dans `/opt/dsoxlab`, cree par un playbook en
    `become: true` et donc possedee par root, alors que les tests tournent en
    ssh sous un compte ordinaire. Un `git commit` y echoue sur les droits, et
    l'epreuve du niveau 1 est sortie ROUGE pour cette seule raison. L'API ne
    touche pas au disque.

    Les champs sont passes en formulaire (`--data-urlencode`), ce qui evite
    d'avoir a construire du JSON dans une ligne de commande.

    LIMITE A CONNAITRE, mesuree le 2026-10-22 : un corps de formulaire ne sait
    pas porter de TABLEAU. `POST /repository/commits`, qui attend un tableau
    d'actions, repond donc « 400 Bad request - actions must be an array », et
    la forme `actions[0][action]=…` n'y change rien. Pour un commit d'un seul
    fichier, `POST /repository/files/:chemin` fait l'affaire avec des champs
    simples. Pour un vrai tableau, il faudra passer du JSON par fichier.
    """
    url = f"{URL}/api/v4{chemin}"
    morceaux = [
        "JETON=$(cat /etc/dsoxlab/jeton-api 2>/dev/null); "
        '[ -n "$JETON" ] || exit 64; '
        "curl -sS --max-time 30 -o /tmp/reponse-api -w '%{http_code}' "
        f"-X {methode} "
        '-H "PRIVATE-TOKEN: $JETON"'
    ]
    for cle, valeur in (champs or {}).items():
        morceaux.append(f"--data-urlencode {shlex.quote(f'{cle}={valeur}')}")
    morceaux.append(shlex.quote(url))
    morceaux.append("; echo; cat /tmp/reponse-api; rm -f /tmp/reponse-api")

    r = host.run(" ".join(morceaux))
    if r.rc != 0:
        return 0, None
    # Le code HTTP est sur la premiere ligne, le corps sur les suivantes.
    tete, _, corps = r.stdout.partition("\n")
    try:
        code = int(tete.strip())
    except ValueError:
        return 0, None
    if not corps.strip():
        return code, None
    try:
        return code, json.loads(corps)
    except json.JSONDecodeError:
        return code, corps


def lint_configuration(host, projet_id: int, ref: str = "main") -> dict | None:
    """Ce que le linter CI de GitLab dit de la configuration de la branche.

    POURQUOI PASSER PAR LUI PLUTOT QUE RELIRE LE YAML. Un pipeline refuse
    apparait « failed » AVEC ZERO JOB, et le champ `yaml_errors` du pipeline
    rend `null` : rien ne dit pourquoi. Le linter, lui, nomme la cause, et
    c'est ainsi qu'a ete trouve un job nomme `image`, mot-cle reserve
    (« image is defined in top-level and `default:` entry »).

    Rend le rapport (`valid`, `errors`, `warnings`), ou None si le linter n'a
    pas repondu : un test ne doit jamais conclure sur une mesure absente.
    """
    rapport = api(
        host,
        f"/projects/{projet_id}/ci/lint",
        f"dry_run=true&ref={ref}",
    )
    return rapport if isinstance(rapport, dict) else None


def projet(host, chemin: str = PROJET) -> dict | None:
    """Le projet de l'apprenant, par son CHEMIN EXACT dans la forge.

    POURQUOI PAS UNE RECHERCHE, mesure le 2026-10-21. `?search=` rend tout ce
    qui CONTIENT le terme. Or un projet supprime n'est pas supprime : GitLab le
    met en retention (30 jours sur cette instance, reglage non modifiable en
    CE) et le renomme en `pipeline-craft-deletion_scheduled-1`. La recherche le
    rend donc encore, et la version precedente de cette fonction, qui retombait
    sur le premier resultat, notait l'etat d'un PROJET MORT : un pipeline
    fantome y restait visible, indestructible, et un test passait grace a lui.

    Un projet encore marque pour suppression est donc ecarte, meme trouve a son
    chemin exact : son etat n'est pas celui que l'apprenant a produit.
    """
    p = api(host, f"/projects/root%2F{chemin}")
    if not isinstance(p, dict) or not p.get("id"):
        return None
    if p.get("marked_for_deletion_on") or p.get("marked_for_deletion_at"):
        return None
    return p


def pipelines(host, ref: str | None = None, projet_id: int | None = None) -> list:
    """Les pipelines du projet, du plus recent au plus ancien."""
    if projet_id is None:
        p = projet(host)
        if p is None:
            return []
        projet_id = p["id"]
    params = "per_page=20&order_by=id&sort=desc"
    if ref:
        params += f"&ref={ref}"
    out = api(host, f"/projects/{projet_id}/pipelines", params)
    return out if isinstance(out, list) else []


def dernier_pipeline(host, ref: str | None = None) -> dict | None:
    """Le pipeline le plus recent, sur `ref` si elle est donnee."""
    tous = pipelines(host, ref)
    return tous[0] if tous else None


def jobs(host, pipeline_id: int, projet_id: int | None = None) -> list:
    """Les jobs d'un pipeline, avec leur nom, leur stage et leur statut."""
    if projet_id is None:
        p = projet(host)
        if p is None:
            return []
        projet_id = p["id"]
    out = api(host, f"/projects/{projet_id}/pipelines/{pipeline_id}/jobs", "per_page=100")
    return out if isinstance(out, list) else []


def statut(host, ref: str | None = None) -> str | None:
    """Le statut du dernier pipeline : success, failed, running, blocked…"""
    p = dernier_pipeline(host, ref)
    return p.get("status") if p else None


def fichier(host, chemin: str, ref: str = "main", projet_id: int | None = None) -> str | None:
    """Le contenu d'un fichier TEL QUE LA FORGE LE SERT, ou None.

    Pourquoi lire dans la forge et pas sur le disque de la VM : un fichier
    corrige localement mais jamais pousse laisse le serveur, et donc le
    pipeline, dans son etat d'avant. C'est l'etat pousse qui compte.

    DEUX PIEGES, ET LE SECOND RENDAIT CETTE FONCTION INUTILISABLE :

      - le chemin s'encode pour l'API, les `/` en `%2F`, ET le point d'un nom
        comme `.gitlab-ci.yml` en `%2E` : sinon GitLab y lit une extension de
        format et rend du JSON a la place du fichier ;
      - l'appel doit demander le texte BRUT. La premiere version appelait
        `api()` sans `brut=True` : la reponse, qui n'est pas du JSON, etait
        jetee au decodage, et la fonction rendait donc TOUJOURS None. Un test
        qui s'y fiait aurait conclu « fichier absent » sur un fichier present.
    """
    if projet_id is None:
        p = projet(host)
        if p is None:
            return None
        projet_id = p["id"]
    encode = chemin.replace("/", "%2F").replace(".", "%2E")
    out = api(
        host,
        f"/projects/{projet_id}/repository/files/{encode}/raw",
        f"ref={ref}",
        brut=True,
    )
    return out if isinstance(out, str) else None


def stages(jobs_du_pipeline: list) -> set[str]:
    """Les stages reellement presents dans un pipeline."""
    return {j.get("stage") for j in jobs_du_pipeline if j.get("stage")}


def noms(jobs_du_pipeline: list) -> set[str]:
    """Les noms de jobs reellement presents."""
    return {j.get("name") for j in jobs_du_pipeline if j.get("name")}


def forge_joignable(host) -> bool:
    """La forge repond-elle ? A appeler avant de conclure a un echec de l'apprenant.

    Sans ce garde-fou, une VM dont GitLab n'a pas fini de demarrer ferait
    echouer tous les tests, et l'apprenant chercherait une faute qu'il n'a pas
    commise. GitLab met plusieurs minutes a repondre au premier demarrage.
    """
    r = host.run(f"curl -sS -o /dev/null -w '%{{http_code}}' --max-time 10 {URL}/-/readiness")
    return r.rc == 0 and r.stdout.strip() == "200"
