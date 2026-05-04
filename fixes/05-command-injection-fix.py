# Fix 05 — Command Injection

## Faille
```python
# ❌ Vulnérable — pas d'échappement de commande shell
import subprocess

@app.route('/ping', methods=['POST'])
def ping():
    host = request.form['host']
    # ← Utiliser directement l'input utilisateur dans une commande shell
    result = subprocess.run(f'ping -c 1 {host}', shell=True, capture_output=True)
    return result.stdout.decode()
```

**Payload d'attaque :**
```
host: 8.8.8.8; cat /etc/passwd
# Exécute : ping -c 1 8.8.8.8; cat /etc/passwd
```

## Fix
```python
# ✓ Sécurisé — pas de shell, arguments séparés
import subprocess
import ipaddress

@app.route('/ping', methods=['POST'])
def ping():
    host = request.form['host']

    # ✓ Valider l'input
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return 'IP invalide', 400

    # ✓ Pas de shell=True, arguments en liste
    result = subprocess.run(['ping', '-c', '1', host], capture_output=True, timeout=5)
    return result.stdout.decode()
```

## Explication
- **Avant :** shell=True + string interpolation = injection possible
- **Après :** shell=False + liste d'arguments = pas d'injection
- **Bonus :** Valider l'IP (regex ou ipaddress)

## Ressources
- [OWASP Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [Subprocess Security](https://docs.python.org/3/library/subprocess.html#security-considerations)
