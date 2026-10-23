# Journal des modifications

Les changements notables de ce catalogue sont consignés ici. Le format suit
[Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), et ce catalogue suit
le [versionnage sémantique](https://semver.org/lang/fr/).

**Ce qu'une version veut dire ici.** Un catalogue n'est pas une bibliothèque :
un incrément MINEUR ajoute des labs, un CORRECTIF corrige un énoncé ou un test
sans changer ce qu'un lab prouve, et un incrément MAJEUR renomme ou retire des
labs, ce qui casse la progression déjà enregistrée des apprenants.

## [0.2.0] - 2026-10-23

### Ajouté

- **Le niveau C4 passe de zéro à sept labs**, et le catalogue de 21 à **29**,
  de 13 h 55 à **20 h 40**. Ce niveau était déclaré VIDE à la publication du
  catalogue hier, et le README le disait plutôt que de le cacher : c'est le
  trou que l'audit du 2026-10-21 avait trouvé. Il est comblé.

  `gl-20-secrets-avances` renouvelle les secrets sans casser le pipeline,
  `gl-21-activer-les-scanners` active les scanners et lit ce qu'ils disent,
  `gl-22-scanner-les-images` empêche une faille critique de partir,
  `gl-23-supply-chain-tracable` signe l'image et refuse celles qui ne le sont
  pas, `gl-24-proteger-les-merges` protège ce qui fusionne et ce qui déploie,
  et `gl-25-durcir-le-pipeline` durcit le runner.

- **Deux épreuves de plus** : `gl-ep3-un-pipeline-qu-on-peut-auditer` ferme le
  niveau C4, et `gl-ep4-un-pipeline-a-industrialiser` ferme le C3 avec un
  pipeline laissé à moitié industrialisé, à diagnostiquer. Le catalogue porte
  désormais quatre labs évalués et un capstone.

- Les vingt-neuf verdicts sont **VALIDE 0 -> 100**, et les vingt-neuf solutions
  de référence sont chiffrées.

### Corrigé

- `gl-ep4-un-pipeline-a-industrialiser` déclare `level: c3` mais `meta.yml` la
  rangeait dans la section C1. Un apprenant qui finissait le niveau 1 tombait
  sur l'épreuve du niveau 3, et `dsoxlab next` suivait cet ordre. Déplacée à la
  fin d'`industrialiser`, où les trois autres épreuves concordent déjà avec
  leur niveau.

- `gl-19-reconstruire-tout-le-pipeline` se déclare `lab_type: capstone` et non
  `lab`. Il part d'un dépôt sans aucune CI, avec un cahier des charges pour
  seul énoncé, et il ferme le niveau C3. Le contrôle `check:niveaux` du site
  refuse qu'un niveau soit validé par un `lab`, et il a raison.

- Les deux épreuves de niveau pointent la page de validation plutôt que
  l'index des labs. Le changement a attendu que la page soit **servie** : elle
  répondait 404 en production alors qu'elle existait déjà sur disque, et
  `validate-structure --check-urls` l'a dit. Un `doc_url` est une promesse
  faite au lecteur depuis `dsoxlab guide`.

- Cinq noms de variables morts dans deux tests (`RUF059`, `B007`), et un faux
  positif de `detect-private-key` sur le lab dont le sujet EST les secrets :
  il écrit un en-tête de clé comme MARQUEUR, dans un `grep -q` et dans
  l'assertion qui le contrôle. Ce lab, et lui seul, est exclu de ce hook ; une
  vraie clé posée dans un autre lab reste refusée, ce qui a été mesuré.

## [0.1.1] - 2026-10-22

### Ajouté

- Un verdict ne peut plus être commité avec ce qu'il mesure. Le hook
  `verdicts-et-commun-separes` refuse un commit portant `validation-labs.json`
  à côté de ce que le cycle joue : `challenge/tests/`, `setup.yaml`,
  `cleanup.yaml`, `lab.yaml` d'un lab, et l'outillage partagé.

  Cela ferme un cas **qu'aucune mesure ne rattrape après coup**. Quand une pull
  request squashée retouche un test *après* sa campagne, le commit unique porte
  les deux et le squash a détruit ce qui les distinguait : ni une date, ni un
  diff entre deux arbres, ni une empreinte inscrite ensuite ne peuvent dire
  lequel est venu avant. Il ne se constate pas, il s'empêche.

  L'énoncé reste autorisé à côté d'un relevé : il n'est pas joué par le cycle,
  et l'interdire obligerait à une campagne pour une coquille.

- `scripts/empreinte_lab.py` et `scripts/verifier-attestations.py`, une
  corroboration locale : un sha256 de ce que le cycle joue, inscrit à côté de
  chaque verdict par les campagnes à venir. Elle n'est **pas exigée** : un
  verdict qui n'en porte pas n'est pas un défaut, le contrôle le dit et sort en
  0. `--strict` rétablit le code 10 pour un appelant automatisé.

### Corrigé

- La péremption d'un verdict ne se juge plus en comparant des **dates**, ce qui
  répond à une autre question que celle qu'on pose. Elle s'est trompée dans les
  deux sens le 2026-10-22 : une correction commitée avec les verdicts qu'elle
  périmait est passée pour saine, et des labs réattestés sur une branche sont
  ressortis « à réattester » après leur fusion en squash, contenu inchangé.

  Les arbres git sont déjà des empreintes de contenu : le contrôle qui fait foi
  compare donc deux arbres, et ne dépend plus de la façon dont on a fusionné.

## [0.1.0] - 2026-10-22

### Ajouté

- **Vingt et un labs sur GitLab CI/CD**, de `gl-01` à `gl-19` plus deux
  épreuves de fin de niveau, `gl-ep1-un-pipeline-qui-dit-vrai` (C1) et
  `gl-ep2-une-livraison-tracable` (C2). Onze heures cinquante-cinq de labs,
  près de quatorze heures avec les deux épreuves.

- **Vingt et un verdicts VALIDE 0 -> 100** dans `validation-labs.json`, chacun
  produit par `scripts/valider-labs.py`, qui exige un score NUL sur l'état de
  départ et cent sur l'état corrigé. Un test qui passe avant le travail ne
  mesure rien, et ce catalogue a commis cette faute quatre fois le premier
  jour.

- **Une VM**, `gitlab-1.lab`, portant GitLab CE 19.5.1 et son runner, posés par
  `labs/_commun/socle.yaml` en cinq minutes trente-quatre au premier passage,
  idempotent ensuite. Le dépôt fil rouge arrive par un bundle git, avec `main`
  et les dix-neuf branches `starter/lab-NN`, jamais les branches `solution/` :
  une solution n'a rien à faire dans la forge qui la note.

- **Trois contrôles qui lui sont propres**, chacun né d'un défaut réel.
  `scripts/check-playbooks.py` charge les quatre-vingt-sept playbooks,
  corrigés chiffrés compris : il attrape un défaut revenu quatre fois, une
  apostrophe française isolée dans un commentaire à l'intérieur d'un bloc
  `ansible.builtin.shell`, qui fait refuser le playbook avec un message qui ne
  nomme ni le fichier ni la cause. `scripts/check-tests.py` nomme les symboles
  ni importés ni définis dans les tests. `dsoxlab validate-structure` tient le
  contrat.

- **La chaîne de contribution des catalogues frères** : Zizmor, Actionlint,
  Poutine, parité pre-commit et CodeQL sur `python` et `actions`, plus Plumber,
  Scorecard, Dependabot et les gabarits d'issue. Six jobs, sept contrôles.

### Corrigé

- `labs/_commun/depot/` est désormais hors de portée de tout hook. Mesuré en
  ajoutant le hook `ruff` : le premier passage de `trailing-whitespace` et
  `end-of-file-fixer` a retiré **12 octets** au bundle git du dépôt fil rouge,
  de 67 018 à 67 006. `git bundle verify` l'acceptait encore, ce qui est pire
  qu'un échec franc : le jour où la coupe tombe ailleurs, les dix-neuf labs
  perdent leur dépôt de départ sans qu'un contrôle le dise.

- Le hook `playbooks-se-chargent` nomme maintenant sa dépendance, `uv run
  --with pyyaml`, comme le hook voisin le faisait déjà. Sans elle, le script
  tournait avec l'interpréteur du système, où pyyaml est absent, ne distinguait
  plus un playbook d'un fichier de tâches, les passait tous à `--syntax-check`
  et en refusait deux à tort. Le hook échouait pendant que le même script
  passait en ligne de commande.

- `ruff` est aligné sur le jeu de règles commun aux catalogues frères plutôt
  que sur un jeu local plus étroit, et il est joué en hook, pas seulement en
  CI. Quarante-neuf écarts sont apparus. Les quarante-deux qui touchaient des
  **tests attestés** sont des directives `# noqa: E402` mortes, laissées en
  place à dessein : rejouer vingt et un labs sur la forge pour supprimer un
  commentaire n'est pas un arbitrage raisonnable, et `per-file-ignores` le dit
  par écrit. Les sept autres, tous dans `scripts/`, sont corrigés.

## [Non publié]

### Ajouté

- Le squelette du catalogue, créé par `dsoxlab new catalog`.
