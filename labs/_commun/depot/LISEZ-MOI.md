# Le depot fil rouge des labs

Un seul fichier utile ici, et c'est voulu : `pipeline-craft.bundle`, un bundle
git du depot fil rouge `pipeline-craft`.

## Pourquoi un bundle, et pas une copie des fichiers

Les 19 pages de lab du site decrivent le depot **reel** : ses chemins
(`app/main.py`, `requirements-dev.txt`), ses messages d'erreur releves a
l'execution, et sa convention de branches `starter/lab-NN`. Une arborescence
reconstruite a cote ferait diverger la consigne de son corrige, et l'apprenant
lirait `app/main.py` sur le site en trouvant autre chose dans la forge.

Le bundle apporte donc le depot tel quel, avec son historique.

## Ce qu'il contient, et ce qu'il ne contient pas

| Dans le bundle | Hors du bundle |
|---|---|
| `main`, l'etat de depart du lab 01 | les branches `solution/*` |
| les 19 branches `starter/lab-NN` | |

Les branches `solution/*` sont la **reponse**. Elles restent cote formateur,
dans le depot source, ou les playbooks de `solution/` vont chercher le corrige
pour prouver que chaque lab se reussit. Pousser la solution dans la forge que
l'on note rendrait la note sans valeur.

## Le refaire

```bash
scripts/fabriquer-bundle.sh                     # depuis ~/Projets/lab-gitlab-cicd
SOURCE=/autre/chemin scripts/fabriquer-bundle.sh
```

Le script verifie le bundle qu'il vient d'ecrire (`git bundle verify`) : un
bundle tronque se pousse sans broncher et casse le lab plus tard, loin de sa
cause.
