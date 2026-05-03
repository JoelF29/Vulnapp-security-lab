# Faille 01 — SQL Injection

## Concept

Quand une application colle directement l'input utilisateur dans une requête SQL,
l'attaquant peut "sortir" du rôle de données et injecter du code SQL arbitraire.
Le résultat : contourner l'authentification, lire des données, modifier ou supprimer la base.

## Code vulnérable

```python
# app.py — route /login
user = db.execute(
    f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
).fetchone()

if user:
    # connecté sans vérification du hash
```

## Exploit

**Payload :** taper `alice'--` dans le champ username, n'importe quoi en password.

La requête générée :
```sql
SELECT * FROM users WHERE username = 'alice'--' AND password = 'faux'
```

- `'` ferme la chaîne username prématurément
- `--` met en commentaire tout le reste (y compris la vérification du password)
- SQLite retourne alice → connexion réussie sans mot de passe

Autres payloads classiques :
```
' OR '1'='1      → retourne le premier utilisateur de la table
' OR 1=1--       → même effet
admin'--         → connexion directe si le username existe
```

## Fix

```python
# Requête paramétrée — le ? isole la donnée du code SQL
user = db.execute(
    'SELECT * FROM users WHERE username = ?', (username,)
).fetchone()

if user and check_password_hash(user['password'], password):
    # connecté seulement si username ET password corrects
```

**Pourquoi ça corrige :**
SQLite reçoit la requête SQL et les données séparément.
L'input utilisateur est traité comme une chaîne brute, jamais comme du code.
`alice'--` devient littéralement le nom cherché — aucun utilisateur ne s'appelle comme ça.

## Classification

- **OWASP Top 10 :** A03:2021 — Injection
- **CWE :** CWE-89 — Improper Neutralization of Special Elements in SQL Commands
- **Impact :** Authentication bypass, data exfiltration, data destruction

## Ressources

- [PortSwigger — SQL Injection](https://portswigger.net/web-security/sql-injection)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
