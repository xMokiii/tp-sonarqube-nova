# TP3 — DAST avec OWASP ZAP

Ce TP complète le [TP SonarQube](../README.md) avec une analyse dynamique de TIWAP.
L'automatisation utilise **GitHub Actions**, selon le choix de l'étudiant.

- [Compte rendu, qualification des alertes, fiches métier et indicateurs](compte-rendu.md)
- [Rapport ZAP HTML du scan local](preuves/zap-report.html)
- [Rapport ZAP JSON du scan local](preuves/zap-report.json)
- [Vérifications HTTP](preuves/http-verification.json)
- [Capture de TIWAP](preuves/tiwap-local.png)
- [Workflow GitHub Actions](../.github/workflows/dast.yml)
- [Exécutions GitHub Actions](https://github.com/xMokiii/tp-sonarqube-nova/actions/workflows/dast.yml)
- [Exécution validée et artefact](https://github.com/xMokiii/tp-sonarqube-nova/actions/runs/38882931903)
- [Capture du workflow réussi](preuves/github-actions-workflow.png)
- [Archive des livrables](../livrables-tp3-zap.zip)

## 1. Démarrer le laboratoire local

Prérequis : Docker Desktop avec les conteneurs Linux, Docker Compose v2 et Git.
Depuis la racine de ce dépôt, dans PowerShell :

```powershell
Set-Location tp3\TIWAP
New-Item -ItemType Directory -Path reports -Force
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Ouvrir <http://localhost:5001> et utiliser le compte pédagogique `admin` / `admin`.
Le projet Docker `nova-tp3-zap` et le port 5001 évitent une collision avec l'autre
laboratoire TIWAP du TP précédent. MongoDB n'est pas publié sur l'hôte.

Cette copie versionnée de TIWAP provient du commit amont
`1f9d2ac01b19c86ed20242fce5556ea77417d2a9`.
Le démarrage Flask utilise HTTP conformément au TP. Les vulnérabilités
pédagogiques restent présentes ; la correction SQL du TP SonarQube est
conservée dans les preuves de cet autre TP et n'est pas appliquée à cette copie.

## 2. Exécuter ZAP et lire les rapports

Depuis `tp3/TIWAP` :

```powershell
docker compose exec -T zap zap-baseline.py -t http://app:5000 -m 2 -r zap-report.html -J zap-report.json
$LASTEXITCODE
Start-Process .\reports\zap-report.html
```

ZAP utilise `app:5000` sur le réseau Docker. `localhost` dans ZAP désignerait
ZAP lui-même. Les noms de fichiers sont relatifs à `/zap/wrk/` : les chemins
absolus du PDF provoquent ici un préfixe doublé et empêchent leur génération.

Le scan local initial contient 15 entrées d'alertes : 4 moyennes, 7 faibles et
4 informationnelles, correspondant à 13 règles et 39 occurrences. L'analyse
et les limites sont détaillées dans le compte rendu. Le baseline anonyme ne
confirme pas d'injection SQL ; la divulgation de texte SQL est un autre constat.

## 3. Automatisation GitHub Actions

Le workflow se déclenche sur `push`, `pull_request` et `workflow_dispatch`.
Le job utilise Ubuntu 24.04 et le Docker du runner ; aucun secret personnel
ni runner GitLab n'est nécessaire pour ce dépôt.

1. Le workflow récupère le code et localise `tp3/TIWAP`.
2. `ci/run-dast.sh` construit l'image et attend MongoDB puis HTTP 200 sur TIWAP.
3. Le baseline cible uniquement le service TIWAP du réseau éphémère du job.
4. `ci/validate-report.py` contrôle les rapports et produit une synthèse réelle.
5. Un code ZAP `2` affiche un avertissement ; un FAIL ou une erreur technique
   échoue. Un rapport manquant ou invalide échoue aussi.
6. Le job nettoie son projet Docker. Les rapports et les journaux sont conservés
   comme artefacts pendant sept jours, même lorsqu'une étape échoue.

Pour les retrouver, ouvrir **Actions > TP3 - DAST OWASP ZAP**, choisir une
exécution, puis télécharger l'artefact `tp3-zap-<run_id>-<tentative>`.
Il contient les rapports HTML/JSON, la synthèse et les journaux de démarrage/scan.
Les règles de risque ZAP ne remplacent pas la qualification métier.

La première exécution réelle a réussi. Ses rapports CI contiennent 16 entrées
(4 moyennes, 7 faibles, 5 informationnelles), 13 règles et 39 occurrences. La
différence avec le scan local est documentée dans le compte rendu.

## 4. Arrêter le laboratoire local

Depuis `tp3/TIWAP` :

```powershell
docker compose down
docker compose ps
```

Les rapports locaux restent dans `reports/`, qui est ignoré par Git. Les preuves
retenues pour le rendu sont conservées séparément dans `tp3/preuves/`.
