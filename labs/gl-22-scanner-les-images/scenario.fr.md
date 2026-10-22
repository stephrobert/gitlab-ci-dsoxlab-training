# Scénario

Le pipeline de `pipeline-craft` construit une image et la publie dans le
registre du projet, sous le tag du commit. Personne ne la regarde.

Elle est pourtant partie en production avec une base ancienne, et cette base
porte une **vulnérabilité critique** connue. Rien dans le pipeline ne l'a dit,
rien ne l'a arrêtée : l'image a été construite, publiée, et le déploiement a
suivi.

Le projet est dans la forge du lab. Une copie du dépôt vous attend sur la
machine, avec deux notes : `REGISTRE-DU-LAB.txt` et `NOTE-EQUIPE-SECURITE.txt`.

## Mission

Quatre temps, et chacun suppose le précédent.

1. **Scanner l'image publiée.** Un job lit l'image que le pipeline vient de
   pousser, et écrit un rapport.
2. **Garder le rapport.** Il doit rester lisible dans la forge, y compris quand
   le job échoue, puisque c'est alors qu'on en a besoin.
3. **Bloquer.** Une vulnérabilité critique fait échouer le pipeline avant tout
   déploiement.
4. **Écarter ce qui l'a été, et seulement cela.** L'équipe sécurité a trié un
   des findings. Consignez son exception, avec sa raison.

## Pourquoi Trivy, et pas le Container Scanning de GitLab

L'instance de ce catalogue est une **GitLab CE**. Le Container Scanning intégré
y produit bien son rapport, mais tout ce qui l'exploite (tableau de bord de
sécurité, rapport de vulnérabilités du projet, règles de merge request) est
réservé aux éditions Premium et Ultimate. Ce lab fait donc avec ce que la
Community Edition donne vraiment : **un artefact JSON** dans le job, que vous
lisez vous-même. Le scanner est **Trivy**, en ligne de commande.

Image à utiliser : `aquasec/trivy:0.58.1@sha256:ab70a02200597efa04748f210f793936eb647cbcdb0ea69cc30b226d6f5a22c7`.

## Ce que Trivy doit savoir

| Option ou variable | Ce qu'elle fait |
|---|---|
| `--format json --output <fichier>` | écrit le rapport complet au format JSON |
| `--severity CRITICAL` | limite l'analyse (et le seuil) à une gravité |
| `--exit-code 1` | fait échouer la commande si des findings restent |
| `--insecure` | autorise un registre qui répond en HTTP |
| `TRIVY_USERNAME`, `TRIVY_PASSWORD` | identifiants du registre, que le job a déjà |

Le détail du registre est dans `REGISTRE-DU-LAB.txt`. Le registre de cette
forge répond en **HTTP**, et le projet est privé : un Trivy qui ne le sait pas
échoue avant d'avoir scanné quoi que ce soit.

## Le piège du rapport perdu

Par défaut, GitLab **ne conserve pas les artefacts d'un job en échec**. Or le
job de scan est fait pour échouer : sans réglage, le pipeline s'arrête, et le
rapport qui explique pourquoi disparaît avec lui. Vous voyez le rouge, vous
n'avez pas la cause.

Le lab note donc que le rapport survit à l'échec, et que le pipeline a bien
échoué **à cause d'une vulnérabilité critique**, pas d'un registre injoignable.

## Le piège de l'exception

Écarter un finding fait disparaître le problème du rapport sans le corriger. Un
attaquant n'espère rien d'autre : une ligne d'exception sans explication passe
la revue, et six mois plus tard personne ne sait plus pourquoi elle est là.

Trivy lit les exceptions dans un fichier **`.trivyignore`**, à la racine du
dépôt. Deux règles pour ce lab :

- **la raison s'écrit à côté de l'exception**, sur les lignes de commentaire
  (`#`) qui précèdent l'identifiant ;
- **seul le finding trié est écarté**. Les autres vulnérabilités critiques n'ont
  été examinées par personne. Les ignorer pour faire passer le pipeline est
  précisément ce que ce lab apprend à reconnaître.

`NOTE-EQUIPE-SECURITE.txt` donne l'identifiant écarté et la raison de la revue.
Cette note est la **prémisse du lab**. Dans une vraie équipe, vous vérifieriez
avant d'écarter : le paquet est-il dans l'image, le code vulnérable est-il
atteignable ? Vous reprenez ici la raison dans vos mots, en vous assurant
qu'elle tient avec ce que le rapport affiche pour ce finding.

## Un pipeline rouge à la fin, c'est normal

Une fois le finding trié écarté, **les autres critiques restent**. Le seuil
continue donc d'arrêter le pipeline : c'est son travail. Corriger vraiment
consiste à changer la **base de l'image** pour une version à jour, ce qui est
la bonne suite mais n'est pas noté ici.

Un pipeline qui passe seulement parce qu'on a tout écarté serait une régression.

## Ce que le lab vérifie

1. le **dernier pipeline** de `main` porte un job de scan qui a laissé un
   **rapport JSON de Trivy** dans ses artefacts ;
2. ce rapport porte sur **l'image du registre de ce projet, au tag du commit**
   de ce pipeline ;
3. un pipeline a **réellement échoué** à cause d'une vulnérabilité critique,
   avec un rapport conservé, et **aucun déploiement** lancé ;
4. `.trivyignore` écarte **le finding trié et lui seul**, avec une **raison**
   d'au moins quatre mots ;
5. le **dernier rapport ne liste plus** ce finding.

## Ce que le lab ne vérifie pas

Ni le nom de votre job, ni le nom de votre étape, ni celui du fichier de
rapport. Ni que la raison que vous écrivez est **vraie** : un contrôle
automatique mesure qu'elle existe, pas qu'elle est juste. C'est le travail
d'une revue humaine.

## Vérifier à la main

Les artefacts d'un job se lisent dans l'interface du projet, ou depuis la VM :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/pipelines?ref=main&per_page=3" \
  | jq -r '.[] | "\(.id) \(.status) \(.sha[0:8])"'
```

Puis, pour lister les findings critiques d'un rapport téléchargé :

```bash
jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL")
  | "\(.VulnerabilityID) \(.PkgName) \(.InstalledVersion)"' trivy-report.json
```

Remplacez `trivy-report.json` par le nom que vous avez donné à votre fichier.
