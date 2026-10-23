# Formation GitLab CI/CD : écrire un pipeline, et prouver ce qu'il fait

**Langue :** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/gitlab-ci-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/gitlab-ci-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/gitlab-ci-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/gitlab-ci-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/gitlab-ci-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/gitlab-ci-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![Licence : CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Vingt-neuf labs pour écrire un pipeline GitLab CI/CD et le garder digne de
confiance : le faire passer au vert, lire ses échecs, faire circuler les
données entre les jobs, sortir les secrets du code, contrôler quand il part,
publier au registre, l'industrialiser, puis le sécuriser. Chaque lab se joue contre une
**vraie instance GitLab CE et son runner**, et il est noté sur l'état du
pipeline qu'il laisse, jamais sur les commandes tapées.

Écrit pour les administrateurs et les ingénieurs DevOps qui héritent d'un
pipeline qu'ils n'ont pas écrit et doivent le maintenir en marche.

## Ce que c'est

À la fin, un apprenant sait prendre un dépôt sans aucune CI et rendre un
pipeline qui construit, teste et publie, qui dit ce qu'il couvre, qui tourne
une fois par changement plutôt que deux, et qui échoue bruyamment plutôt qu'en
silence. Chacun de ces points est prouvé par des tests qui interrogent la forge
par son API, pas par la lecture du `.gitlab-ci.yml` que l'apprenant a écrit.

**L'ordre compte, et ce n'est pas celui des sujets.** Il suit ce dont un
pipeline a besoin avant que l'étape suivante soit seulement possible : un
pipeline vert avant de lire un échec, un échec lu avant de choisir une image,
des artifacts avant de publier, la publication avant l'industrialisation. Le
niveau 2 suppose un pipeline qui marche et demande ce qui se passe quand il
dérape ; le niveau 3 suppose qu'on sait le réparer et demande comment le rendre
rapide, factorisé et fiable.

`dsoxlab next` suit cet ordre, dérivé de la position de chaque lab dans
`meta.yml`.

### Ce que les tests font, et ce qu'ils refusent de faire

**Un lab est noté sur l'état laissé sur la forge, jamais sur les commandes
tapées.**

Les tests interrogent GitLab par son API : les pipelines qui ont réellement
tourné, leurs jobs, leurs statuts, les étiquettes du registre, les rapports
attachés à une demande de fusion. Ils ne lisent pas le YAML écrit par
l'apprenant.

```python
# NON : on relit ce que l'apprenant a écrit, ce qui ne prouve rien
assert "needs:" in gitlab_ci_yml

# OUI : on demande à la forge ce qui s'est réellement passé
jobs = api(f"/projects/{pid}/pipelines/{pipeline}/jobs")
assert {j["name"] for j in jobs if j["status"] == "success"} >= attendus
```

Le piège ainsi évité est celui du pipeline vert qui ne fait rien. Un
`.gitlab-ci.yml` avec un seul job `echo ok` passe au vert et ne prouve rien :
les épreuves exigent donc plusieurs jobs réussis couvrant des gestes distincts,
déduits du journal des jobs et non de leur nom.

## Prérequis

Un prérequis manquant coûte une heure de recherche à l'apprenant, donc cette
liste est exacte et mesurée sur `meta.yml`.

- **Python 3.11+ et [`uv`](https://docs.astral.sh/uv/)**
- **`git`**
- **`dsoxlab`**, le moteur, installé en outil autonome (voir plus bas)
- **`terraform`** et **`ansible-playbook`**, dont tout lab `vm` a besoin
- **libvirt/KVM 8.0 ou plus**, l'hyperviseur qui porte la machine

Rien de GitLab n'est nécessaire sur ton poste : le lab installe GitLab CE et
son runner dans la machine virtuelle, ce qui est justement l'objet du socle
joué avant le premier lab.

**Les vingt-neuf labs sont des labs `vm`**, donc `dsoxlab provision` est
toujours nécessaire.

### La machine, et pourquoi elle est grosse

Une machine virtuelle, déclarée dans [`meta.yml`](./meta.yml) sur le réseau
`lab-gitlab-ci` (`10.10.95.0/24`) :

| Hôte | Distribution | vCPU | RAM | Disque |
|---|---|---|---|---|
| `gitlab-1.lab` | Ubuntu 24.04 | 4 | 8 Go | 50 Go |

GitLab CE n'est pas un petit service : 8 Go de RAM et 4 vCPU sont ce qu'il faut
pour ses propres composants, son runner, et les conteneurs que les jobs
démarrent. Le socle est posé par `labs/_commun/socle.yaml` en cinq minutes et
demie au premier passage, et il est idempotent ensuite.

Le dépôt fil rouge arrive par un **bundle git**, avec `main` et les dix-neuf
branches `starter/lab-NN`. Les branches `solution/` ne sont jamais poussées :
une solution n'a rien à faire dans la forge qui la note.

`dsoxlab doctor` dit ce dont ce dépôt a besoin et ce dont il n'a pas besoin, et
distingue un contrôle qui a échoué d'un contrôle qu'il n'a pas pu mesurer.

## Installation

`dsoxlab` est publié sur [PyPI](https://pypi.org/project/dsoxlab/).
Installe-le en outil autonome, pour qu'il reste hors de ce dépôt :

```bash
# 1. La CLI dsoxlab (outil externe, hors de ce dépôt)
uv tool install dsoxlab

# 2. Ce catalogue de labs
git clone https://github.com/stephrobert/gitlab-ci-dsoxlab-training.git
cd gitlab-ci-dsoxlab-training

# 3. Vérifier le contrat et la machine
dsoxlab validate-structure
dsoxlab doctor
```

### Votre premier lab, en cinq minutes

La machine doit exister d'abord : rien ici ne tourne sur ton poste.

```bash
export LAB_HOME=$PWD
dsoxlab provision                        # crée gitlab-1.lab, une fois

dsoxlab list-labs                        # les vingt-neuf labs, dans l'ordre
dsoxlab run       gl-01-premier-pipeline # pose l'état de départ et ouvre la session
dsoxlab challenge gl-01-premier-pipeline # lire la mission, sans pas-à-pas
dsoxlab check     gl-01-premier-pipeline # joue les tests, enregistre le score

dsoxlab clean     gl-01-premier-pipeline # défait le lab, garde la machine
dsoxlab destroy                          # rend la machine
```

C'est `run` qui prépare le lab. Un `check` joué sur un lab jamais démarré ne
mesure rien, et le dit au lieu d'enregistrer un 0. `provision` sort en code non
nul si l'hôte ne répond pas, et nomme les domaines orphelins qu'il a laissés
plutôt que d'annoncer un succès.

### Garder à jour

```bash
uv tool upgrade dsoxlab        # le moteur, publié sur PyPI
git -C <ce dépôt> pull         # le catalogue
```

Le moteur et le catalogue avancent indépendamment : un nouveau `dsoxlab`
n'oblige jamais à recloner les labs, et de nouveaux labs n'obligent pas à
mettre l'outil à jour, tant que la version du contrat correspond.

## Comment ça marche

### Le contrat déclaratif, à deux niveaux

Ce dépôt n'est **pas** la CLI. Un défaut du moteur se corrige dans
[dsoxlab](https://github.com/stephrobert/dsoxlab), ou s'y signale par une
issue. Ici, tout ce qui pilote la CLI est déclaratif :

- **`meta.yml`** à la racine déclare l'identité du dépôt, l'**infrastructure**
  (provider, réseau `lab-gitlab-ci`, `10.10.95.0/24` et l'hôte
  `gitlab-1.lab`) et l'**ordre** des sections affichées par `list-labs` ;
- **`lab.yaml`** par lab déclare ses `skills`, son `level`, son `runtime`, ses
  `distros`, son `doc_url` et un bloc `validation`. Un `lab.fr.yaml` surcharge
  `title` et `description` en français, et rien d'autre ;
- **`setup.yaml`** et **`cleanup.yaml`** posent et défont l'état de la forge ;
- **`challenge/tests/test_functional.py`** porte la preuve.

Les gabarits Terraform et cloud-init sont **packagés dans dsoxlab**, pas ici :
ce dépôt ne déclare que son bloc `infra:` et sa clé publique dans `ssh/`.

### Le cycle de vie d'un lab

```bash
dsoxlab list-labs              # parcourir le catalogue
dsoxlab show      <id>         # métadonnées et état d'un lab
dsoxlab run       <id>         # poser l'état initial et ouvrir la session
dsoxlab challenge <id>         # lire la mission, sans pas-à-pas
dsoxlab hint      <id>         # révéler un indice (déduit du score)
dsoxlab check     <id>         # jouer les tests, calculer et enregistrer le score
dsoxlab submit    <id>         # pour les deux épreuves : un verdict, pas un score
dsoxlab clean     <id>         # défaire le lab, garder la machine
dsoxlab progress               # progression par section, score moyen
```

### Le modèle de validation

La validation **prouve l'état, elle ne fait pas confiance**, et un lab est
prouvé **dans les deux sens** : les tests doivent échouer avant le travail et
passer après. Un test vert avant le travail n'est pas un test, c'est une
hypothèse sur le setup. Ce catalogue a commis cette faute quatre fois le
premier jour, et c'est pourquoi `scripts/valider-labs.py` exige **0 avant et
100 après** et inscrit le verdict dans
[`validation-labs.json`](./validation-labs.json).

Les solutions de référence vivent dans `solution/<lab>/solution.yaml`, et les
**vingt-neuf sont chiffrées** par `ansible-vault`. Une solution livrée en
clair gâche le lab, et git la garde pour toujours.

Trois contrôles propres à ce dépôt, chacun né d'un défaut réel :

| Contrôle | Ce qu'il a attrapé |
|---|---|
| `scripts/check-playbooks.py` | une apostrophe française isolée dans un commentaire, à l'intérieur d'un bloc `ansible.builtin.shell`, fait refuser le playbook par Ansible, avec un message qui ne nomme ni le fichier ni la cause. Revenu quatre fois. |
| `scripts/check-tests.py` | un symbole ni importé ni défini dans un test : il lève à l'exécution et note l'apprenant 0, sans que rien n'accuse le test. |
| `dsoxlab validate-structure` | le contrat déclaratif, les liens, le barème et la parité de langue. |

## Catalogue

Vingt-neuf labs, **20 h 40** en tout, répartis sur quatre niveaux qui suivent
la formation qu'ils valident.

### Niveau 1 : écrire un pipeline et lire ses échecs

Sept labs et une épreuve, 5 h 05.

| Lab | Ce qu'il prouve |
|---|---|
| `gl-01-premier-pipeline` | un pipeline a réellement tourné sur la branche par défaut, vert, avec au moins trois jobs réussis répartis sur plusieurs stages |
| `gl-02-lire-un-echec` | l'échec est lu dans le journal du job et corrigé, pas contourné |
| `gl-03-images-et-runners` | chaque job tourne sur l'image que son travail demande, et le runner le prend |
| `gl-04-artifacts-et-cache` | les dépendances sont en cache et le rapport de tests survit au job |
| `gl-05-sortir-les-secrets` | aucun secret ne reste dans le dépôt, et le pipeline marche toujours |
| `gl-06-controler-execution` | chaque job part quand il doit, et le déploiement est retenu |
| `gl-07-valider-avant-de-pousser` | le pipeline est validé avant d'atteindre la forge |
| `gl-ep1-un-pipeline-qui-dit-vrai` | **évalué** : quatre défauts à trouver dans un pipeline qui a l'air vert |

### Niveau 2 : livrer

Quatre labs et une épreuve, 3 h 10.

| Lab | Ce qu'il prouve |
|---|---|
| `gl-08-declencher-autrement` | un pipeline part par planification, par l'API et depuis un autre projet |
| `gl-09-publier-au-registre` | l'image est dans le registre, avec l'étiquette du commit |
| `gl-10-rapports-de-qualite` | les rapports s'affichent là où le relecteur regarde |
| `gl-11-diagnostiquer-un-job-bloque` | deux pannes muettes : rien ne tourne, et rien ne se plaint |
| `gl-ep2-une-livraison-tracable` | **évalué** : une livraison qu'on peut retracer jusqu'à son commit |

### Niveau 3 : industrialiser

Huit labs et une épreuve, 6 h 50.

| Lab | Ce qu'il prouve |
|---|---|
| `gl-12-accelerer-le-pipeline` | un cache réellement réemployé, et des jobs qui cessent d'attendre pour rien |
| `gl-13-factoriser-le-yaml` | le pipeline cesse de se répéter, sans changer ce qu'il fait |
| `gl-14-externaliser-les-jobs` | un orchestrateur, et un fichier par étape |
| `gl-15-une-matrice-de-tests` | plus d'une combinaison testée à la fois |
| `gl-16-un-pipeline-enfant` | un pipeline qui génère et joue ses propres jobs |
| `gl-17-un-seul-pipeline-par-changement` | un changement, un pipeline, pas deux |
| `gl-18-fiabiliser-sans-masquer` | fiable sans masquer les échecs derrière une relance |
| `gl-19-reconstruire-tout-le-pipeline` | **capstone** : tout le pipeline reconstruit depuis un cahier des charges |
| `gl-ep4-un-pipeline-a-industrialiser` | **évalué** : un pipeline laissé à moitié industrialisé, à diagnostiquer |

### Niveau 4 : sécuriser et outiller

Six labs et une épreuve, 5 h 35. **Ce niveau était vide à la publication du
catalogue, le 2026-10-22**, et le README le disait plutôt que de le cacher.
C'est le trou que l'audit du 2026-10-21 avait trouvé, et il est comblé.

| Lab | Ce qu'il prouve |
|---|---|
| `gl-21-activer-les-scanners` | les scanners tournent, et leurs rapports sont lus |
| `gl-22-scanner-les-images` | l'image est scannée, et une faille critique cesse de partir |
| `gl-23-supply-chain-tracable` | l'image est signée, et celles qui ne le sont pas sont refusées |
| `gl-20-secrets-avances` | les secrets se renouvellent sans casser le pipeline |
| `gl-24-proteger-les-merges` | ce qui fusionne et ce qui déploie sont protégés |
| `gl-25-durcir-le-pipeline` | le runner est durci, et ce qui était grand ouvert est fermé |
| `gl-ep3-un-pipeline-qu-on-peut-auditer` | **évalué** : un pipeline qu'on peut auditer |

## Contribuer

Lire [`CONTRIBUTING.md`](./CONTRIBUTING.md). En résumé : un lab est prouvé
**dans les deux sens** avant d'être fusionné, `dsoxlab validate-structure` est
vert, et l'énoncé existe en anglais et en français.

Un verdict ne se commite jamais avec le code partagé qu'il mesure : le contrôle
de péremption compare des dates de commit, et un verdict écrit dans le même
commit que `labs/_commun/` ne laisse rien à comparer. Un hook l'impose.

## Licence

Voir [`LICENSE`](./LICENSE).
