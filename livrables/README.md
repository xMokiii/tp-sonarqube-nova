# Livrables du TP SonarQube — NOVA SERVICES

Ouvrir `compte-rendu.md` pour le rapport et les liens vers les preuves.

La correction porte sur la seule fonction `sqli_medium`. Les quatre tests de
régression passent. La seconde analyse SonarQube a réussi, avec les mêmes
51 anomalies que l'analyse initiale ; aucune alerte SQL n'a été inventée.

Ce dossier contient les pièces à remettre, sans fichier `.env`, jeton, mot de
passe, dépôt Git ni clé privée TIWAP. Le dépôt complet de l'application n'est
pas inclus. Les exemples présents dans les descriptions de règles sont les
exemples génériques fournis par SonarQube.

## Rejouer les tests dans une copie du dossier

Depuis ce dossier, avec Git et Python installés :

```powershell
git clone https://github.com/tombstoneghost/TIWAP.git
git -C TIWAP switch --detach 1f9d2ac01b19c86ed20242fce5556ea77417d2a9
Copy-Item sonar-project.properties TIWAP/sonar-project.properties
git -C TIWAP switch -c fix/sql-injection-lab
git -C TIWAP apply ../preuves/correction-sql.patch
python -m unittest discover -s tests -v
```

Les tests utilisent SQLite en mémoire et ne démarrent pas l'application Flask.
Le dépôt amont pouvant évoluer, les commandes sélectionnent le commit de référence
du TP avant d'appliquer la correction.

## Rejouer une analyse

Créer localement un fichier `.env` définissant `POSTGRES_PASSWORD` et
`SONAR_TOKEN`, sans ajouter ce fichier aux livrables. Démarrer uniquement
SonarQube et PostgreSQL, attendre le statut `UP`, puis lancer le scanner :

```powershell
docker compose up -d db sonarqube
docker compose run --rm scanner
```

Le jeton doit être créé dans cette instance SonarQube et autorisé à analyser
le projet `tiwap`. Le fichier Compose de TIWAP n'est pas utilisé.

Pour analyser le fichier SQL initial à la place de la correction :

```powershell
docker compose run --rm -v "${PWD}/preuves/SQLi-avant.py.txt:/usr/src/vulnerabilities/SQLi.py:ro" scanner
```

Le laboratoire source a été arrêté avec `docker compose down`, sans suppression
des volumes. Les résultats exportés restent consultables dans `preuves/`.
