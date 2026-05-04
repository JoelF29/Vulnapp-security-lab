# Faille 07 — Credentials AWS hardcodés

## Concept

Les credentials AWS (clés d'accès) sont hardcodés directement dans le code source.
Quand le code remonte sur GitHub, les scanners automatisés les trouvent en quelques heures.
L'attaquant a alors accès à **toute l'infrastructure AWS** — bien plus que l'app.

## Code vulnérable

```python
# app.py — visible sur GitHub
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION = "eu-west-1"
```

## Exploit

Un scanner du darknet trouve ces credentials en quelques heures après push.
L'attaquant utilise `aws configure` avec ces clés et a accès immédiat à :
- Tous les buckets S3 (lire/modifier/supprimer)
- Bases de données RDS, DynamoDB
- Instances EC2 (lancer du crypto-mining pour $10k/jour)
- Modifier les politiques IAM pour créer des portes dérobées permanentes

**Capital One 2019 :** credentials exposés + misconfiguration S3 = 80M clients compromis, $80M d'amende.

## Fix

```python
# app.py — jamais de secrets en dur
from dotenv import load_dotenv
import os

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'eu-west-1')
```

Fichier `.env` local (ignored par git) :
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=wJal...
AWS_REGION=eu-west-1
```

Fichier `.env.example` (pushé sur GitHub — template sans secrets) :
```
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=eu-west-1
```

**Pourquoi ça corrige :**
- Le code ne contient aucun secret — peut être pushé sans risque
- Les credentials sont en `.env` (ignored par git) — reste local ou sur le serveur seulement
- `.env.example` montre la structure pour les développeurs

## En production

Sur un serveur Heroku/AWS/GCP, les secrets sont stockés via l'interface de déploiement,
jamais dans les fichiers. L'app les récupère via `os.getenv()`.

## Classification

- **OWASP Top 10 :** A02:2021 — Cryptographic Failures
- **CWE :** CWE-798 — Use of Hard-Coded Credentials
- **Impact :** Accès à l'infra cloud complète, coûts énormes, vol de données massif

## Ressources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Capital One 2019 Case Study](https://www.justice.gov/usao-wdwa/pr/seattle-man-sentenced-eight-years-prison-theft-millions-capital-one-customers)
