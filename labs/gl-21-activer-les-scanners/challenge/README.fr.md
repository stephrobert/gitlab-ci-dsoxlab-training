# Challenge : activer les scanners, et lire ce qu'ils disent

## Mission

Le projet `pipeline-craft` est dans la forge du lab, sur
`http://gitlab-1.lab/root/pipeline-craft`, et une copie du dépôt attend dans
`/opt/dsoxlab/gl-21/pipeline-craft` sur la VM, sur la branche `main`.

Le pipeline lance les tests et rien d'autre. Activez SAST et Secret Detection,
lisez les rapports, corrigez le défaut qu'ils désignent.

## Objectif (état attendu)

1. Un job **SAST** a réussi et déposé son rapport.
2. Un job **Secret Detection** a réussi et déposé son rapport.
3. Un rapport de Secret Detection **désigne le jeton** écrit dans le code.
4. Le jeton n'est **plus dans le code**, et le pipeline du dernier commit de
   `main`, lancé par un push, le confirme.
5. `LECTURE.md`, à la racine de `main`, nomme **le fichier et la ligne** du
   rapport.

## Les trois temps

1. ajouter les deux templates et attendre le pipeline ;
2. lire les rapports, y compris celui d'un scan de l'historique ;
3. corriger, pousser, laisser le pipeline du push confirmer.

## Le lab tourne sur une édition Community

Pas de Security Dashboard ni de rapport de vulnérabilités dans l'interface : ce
sont des fonctions Ultimate. Le rapport est le fichier JSON du job. Pour le
lire, deux chemins.

Depuis la page du job, le bouton **Browse** ouvre ses artefacts, où se trouve
`gl-secret-detection-report.json`. Depuis la VM :

```bash
JETON=$(sudo cat /etc/dsoxlab/jeton-api)
API=http://gitlab-1.lab/api/v4/projects/root%2Fpipeline-craft
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/jobs?per_page=20" \
  | jq -r '.[] | "\(.id) \(.name) \(.status)"'
curl -s -H "PRIVATE-TOKEN: $JETON" "$API/jobs/<ID>/artifacts/gl-secret-detection-report.json" \
  | jq '.vulnerabilities[] | {fichier: .location.file, ligne: .location.start_line, regle: .name}'
```

Si le chemin du fichier répond 404, téléchargez l'archive complète et ouvrez-la :

```bash
curl -s -H "PRIVATE-TOKEN: $JETON" -o artefacts.zip "$API/jobs/<ID>/artifacts"
python3 -m zipfile -e artefacts.zip rapport && ls rapport
```

## Si le scan ne voit pas le jeton

Un scan de push examine les commits qu'il reçoit, et le jeton est plus ancien.
Un pipeline lancé à la main relit l'historique : **Build > Pipelines > New
pipeline**, branche `main`, variable `SECRET_DETECTION_HISTORIC_SCAN` à `true`.
C'est une opération **unique**, à ne jamais laisser dans `.gitlab-ci.yml`.

## Trois rappels

- les jobs de scanner sont **lents** au premier passage : le runner télécharge
  leurs images, et il faut qu'il atteigne internet ;
- un rapport SAST **vide** est un résultat valide : le scan a tourné, il n'a
  rien trouvé ;
- retirer le jeton du code **ne l'efface pas** de l'historique : on le tient pour
  compromis, donc à révoquer.

## Validation

```bash
dsoxlab check gl-21-activer-les-scanners
```
