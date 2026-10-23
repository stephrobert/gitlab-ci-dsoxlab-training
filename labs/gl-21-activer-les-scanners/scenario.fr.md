# Scénario

Le pipeline du projet est vert, et c'est ce qui inquiète.

Il lance les tests de l'application, et c'est tout. Personne n'a jamais regardé
ce que contient le code d'un point de vue sécurité, ni ce que l'historique du
dépôt a laissé traîner. Un audit approche, et la question posée est simple :
**qu'est-ce qu'un scanner dirait de ce dépôt aujourd'hui ?**

Il y a une réponse, et elle est dans le code. Quelqu'un a un jour écrit un
secret là où il ne devait pas, et l'application a continué de marcher : un
défaut qui ne casse rien ne se voit pas à la lecture, c'est le propre de ce
genre de faille.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine.

## Mission

1. **Activer deux scanners de sécurité** sur le pipeline : l'analyse statique du
   code (**SAST**) et la détection de secrets (**Secret Detection**).
2. **Lire leurs rapports.** Ce sont des fichiers JSON déposés par les jobs, et
   pas autre chose : l'instance du lab est une GitLab **Community Edition**, qui
   n'a ni tableau de bord de sécurité ni rapport de vulnérabilités dans
   l'interface. Ces fonctions existent dans l'édition Ultimate ; ici, le
   rapport est un fichier, et le lire fait partie du métier.
3. **Corriger le défaut que le scanner désigne**, puis laisser un nouveau scan
   constater qu'il a disparu.
4. **Consigner ce que le rapport a dit** dans un fichier `LECTURE.md` à la racine
   du dépôt : le fichier et la ligne.

## Ce que les scanners rendent, et ce qu'ils ne rendent pas

Un scanner de GitLab est un **job** comme un autre. Il s'ajoute au pipeline par
un template, tourne dans une image que le runner télécharge, et dépose son
résultat en **artefact**. Les jobs `semgrep-sast` (SAST) et `secret_detection`
(Secret Detection) déposent chacun un fichier, `gl-sast-report.json` et
`gl-secret-detection-report.json`.

Le fichier est un JSON dont l'essentiel tient dans une liste, `vulnerabilities`.
Chaque entrée dit **où** (`location.file`, `location.start_line`), **quoi** (le
nom et l'identifiant de la règle) et **à quel point** (`severity`). Une liste
**vide** est un résultat : le scan a tourné, il n'a rien trouvé. Un job qui n'a
jamais tourné, lui, ne dit rien du tout, et c'est une différence que les tests
du lab font.

Un scanner de secrets est un détective, pas un coffre-fort. Il signale un
secret **déjà commité** ; il ne le retire pas de l'historique, et rien d'autre
ne le fera : un jeton qui a été poussé est un jeton **compromis**, qu'on
**révoque** et qu'on remplace.

## Un piège de lecture : ce que le scan de Secret Detection regarde

Un pipeline lancé par un push examine les commits que ce push apporte. Si le
secret a été commité **avant** celui qui active le scanner, ce premier scan peut
ne pas le voir. Le scénario est celui d'une équipe qui active la détection sur
un dépôt déjà ancien, et la parade est un geste ponctuel : un pipeline lancé à
la main pour relire **tout l'historique**. Ce scan-là est une opération
**unique**. Laissé dans la configuration, il rallongerait chaque pipeline, et
il retrouverait indéfiniment un jeton que personne ne peut effacer du passé.

## Ce que le lab vérifie

1. **SAST a tourné** : un job réussi a déposé un rapport de type `sast`, lisible.
2. **Secret Detection a tourné** : un job réussi a déposé un rapport de type
   `secret_detection`, lisible.
3. **Un scan a vu le défaut** : un rapport, quel que soit le pipeline qui l'a
   produit, désigne le jeton écrit dans le code. Effacer la ligne sans avoir
   lancé le scanner ne suffit donc pas.
4. **Le défaut est corrigé et un nouveau scan le confirme** : le fichier existe
   toujours et ne contient plus le jeton, et le pipeline du dernier commit de
   `main`, lancé par un push, a un rapport de secrets qui ne le désigne plus.
   Aucun job de ce pipeline n'a échoué, et le test de l'application passe
   toujours.
5. **La lecture est consignée** : `LECTURE.md` nomme le fichier et la ligne que
   le rapport a désignés.

## Ce que le lab ne vérifie pas

Ni le nom de vos jobs, ni la manière dont vous rangez le secret, ni le nombre de
vulnérabilités du rapport SAST. Le lab ne peut pas non plus savoir si vous avez
**révoqué** le jeton : ce geste se fait dans le service qui l'a émis, et
personne d'autre que vous ne peut le constater. Ici, le jeton est fabriqué et ne
donne accès à rien, mais le réflexe, lui, est ce qui compte.
