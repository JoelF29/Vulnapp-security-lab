# VulnApp — Laboratoire de Sécurité Web

> **Application web intentionnellement vulnérable** construite à des fins pédagogiques.
> Ne jamais déployer en production. Voir [DISCLAIMER.md](DISCLAIMER.md).

Projet réalisé dans le cadre d'un apprentissage autonome en cybersécurité et cloud security.
Chaque faille est documentée avec son concept, son exploit concret et son correctif.

## Stack technique

- **Backend** : Python 3 / Flask
- **Base de données** : SQLite
- **Frontend** : HTML / CSS (no framework)

## Installation

```bash
# Cloner le repo
git clone <url>
cd app_vulnérable

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Linux / macOS

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
# → http://127.0.0.1:5000
```

**Comptes de test :** `alice / password123` — `bob / hunter2`

---

## Failles couvertes

### Fondations Cybersécurité (OWASP Top 10)

| # | Faille | Route | Doc | Fix |
|---|--------|-------|-----|-----|
| 1 | **SQL Injection** — contourner le login sans mot de passe | `/login` | [vulns/01-sql-injection.md](vulns/01-sql-injection.md) | [fixes/01-sql-injection-fix.py](fixes/01-sql-injection-fix.py) |
| 2 | **Broken Authentication** — sessions mal gérées, tokens prévisibles | `/login` | [vulns/02-broken-auth.md](vulns/02-broken-auth.md) | [fixes/02-broken-auth-fix.py](fixes/02-broken-auth-fix.py) |
| 3 | **XSS (Cross-Site Scripting)** — injecter du JS dans le navigateur d'un autre user | `/comments` | [vulns/03-xss.md](vulns/03-xss.md) | [fixes/03-xss-fix.py](fixes/03-xss-fix.py) |
| 4 | **IDOR** — accéder au profil de n'importe quel utilisateur via l'URL | `/profile/<id>` | [vulns/04-idor.md](vulns/04-idor.md) | [fixes/04-idor-fix.py](fixes/04-idor-fix.py) |
| 5 | **Command Injection** — exécuter des commandes système depuis l'app | `/ping` | [vulns/05-command-injection.md](vulns/05-command-injection.md) | [fixes/05-command-injection-fix.py](fixes/05-command-injection-fix.py) |
| 6 | **Unrestricted Upload** — uploader un fichier malveillant sans validation | `/upload` | [vulns/06-upload.md](vulns/06-upload.md) | [fixes/06-upload-fix.py](fixes/06-upload-fix.py) |

### Cloud Security

| # | Faille | Concept | Doc |
|---|--------|---------|-----|
| 7 | **Hardcoded AWS Credentials** — clés AWS exposées dans le code | Secret management | [vulns/07-hardcoded-creds.md](vulns/07-hardcoded-creds.md) |
| 8 | **Exposed Environment Secrets** — variables d'environnement accessibles | Env security | [vulns/08-env-secrets.md](vulns/08-env-secrets.md) |
| 9 | **SSRF** — forcer le serveur à requêter des ressources internes | Faille Capital One 2019 | [vulns/09-ssrf.md](vulns/09-ssrf.md) |
| 10 | **Over-permissive IAM** — rôle AWS trop permissif | Least privilege | [vulns/10-iam-misconfiguration.md](vulns/10-iam-misconfiguration.md) |
| 11 | **Public S3 Bucket** — bucket S3 accessible sans restriction | S3 hardening | [vulns/11-s3-public.md](vulns/11-s3-public.md) |

---

## Structure du repo

```
app_vulnérable/
├── app.py              # Application Flask principale
├── requirements.txt
├── templates/          # Templates HTML
├── static/             # CSS
├── vulns/              # Documentation de chaque faille (concept + exploit)
├── fixes/              # Code corrigé pour chaque faille
├── uploads/            # Répertoire d'upload (faille 6)
├── README.md
└── DISCLAIMER.md
```

---

## Ressources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)
- [DVWA](https://dvwa.co.uk/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security) — labs gratuits
