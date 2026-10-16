# TP SonarQube — NOVA SERVICES

Le [TP3 — DAST avec OWASP ZAP](tp3/README.md) complète ce travail : laboratoire
TIWAP, rapports, analyse des alertes et automatisation avec
[GitHub Actions](https://github.com/xMokiii/tp-sonarqube-nova/actions/workflows/dast.yml).

Analyse statique de TIWAP avec SonarQube et PostgreSQL dans Docker, revue des
résultats et correction ciblée d'une injection SQL, sans lancer l'application
vulnérable.

## Résultats et livrables

- [Compte rendu complet](compte-rendu.md)
- [Dossier à remettre](livrables/README.md)
- [Archive des livrables](livrables-tp-sonarqube-nova.zip)
- [Résultats initiaux](preuves/sonarqube-initial.json) et [après correction](preuves/sonarqube-apres.json)
- [Comparaison structurée](preuves/comparaison.json)
- [Correction SQL](preuves/correction-sql.patch) et [tests de régression](tests/test_sql_injection.py)

La correction de `sqli_medium` est validée par quatre tests. Les deux analyses
SonarQube comptent 51 anomalies : l'injection ciblée n'était pas signalée par
l'outil et a été confirmée par la revue du code et les tests. Le rapport explique
les résultats et les limites de cette comparaison.

## Reconstituer le code et rejouer les tests

Le dépôt amont TIWAP reste séparé et est ignoré par ce dépôt. Depuis la racine
du TP, avec Git et Python installés, exécuter dans PowerShell :

```powershell
git clone https://github.com/tombstoneghost/TIWAP.git
git -C TIWAP switch --detach 1f9d2ac01b19c86ed20242fce5556ea77417d2a9
Copy-Item livrables/sonar-project.properties TIWAP/sonar-project.properties
git -C TIWAP switch -c fix/sql-injection-lab
git -C TIWAP apply ../preuves/correction-sql.patch
python -m unittest discover -s tests -v
```

Les tests utilisent SQLite en mémoire et ne démarrent pas Flask.

## Consulter ou relancer SonarQube

Créer localement un fichier `.env` définissant `POSTGRES_PASSWORD` et, pour
le scanner, `SONAR_TOKEN`. Ce fichier est ignoré par Git. Le jeton doit être
créé dans l'instance SonarQube utilisée et autorisé à analyser le projet `tiwap`.

```powershell
docker compose up -d db sonarqube
```

Attendre le statut `UP` sur `http://127.0.0.1:9000/api/system/status`, puis lancer
une analyse avec :

```powershell
docker compose run --rm scanner
```

Le laboratoire a été arrêté après les analyses, en conservant ses volumes.
Pour l'arrêter après consultation :

```powershell
docker compose down
```

Le fichier Compose de TIWAP n'est pas utilisé. Les jetons et mots de passe locaux
ne sont pas inclus dans les livrables.
