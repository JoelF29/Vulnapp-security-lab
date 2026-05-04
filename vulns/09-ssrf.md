# Faille 09 — SSRF (Server-Side Request Forgery)

## Concept

L'app a une fonction qui prend une URL en paramètre et la requête **depuis le serveur** (pas le navigateur).

Exemple vulnérable :
```python
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    response = requests.get(url)  # ← pas de validation
    return response.text
```

**Le problème :** Si l'utilisateur contrôle l'URL, il peut forcer le serveur à requêter :
- Des ressources **internes** (normalement inaccessibles depuis l'extérieur)
- Des services sur le réseau local
- Le **metadata service AWS** (si on est sur une instance EC2)

## Exploit

### Local (sur ta machine)
```
GET /fetch?url=http://127.0.0.1:5000/internal-api/admin-key
```
→ L'app requête sa propre API "interne" et retourne la clé secrète

### Sur AWS (instance EC2)
```
GET /fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2-instance-role
```
→ L'app accède au metadata service AWS et récupère les credentials temporaires de l'instance

### Attaque réseau
Si la base de données écoute sur `127.0.0.1:3306` :
```
GET /fetch?url=http://127.0.0.1:3306
```
→ L'app requête la base de données directement

## Code vulnérable (AVANT)

```python
@app.route('/fetch')
def fetch_url():
    # FAILLE 09 — SSRF
    url = request.args.get('url', '')
    response = requests.get(url, timeout=5)
    return f'<pre>{response.text}</pre>'
```

## Fix

**Règle 1 — Bloquer les IPs privées/réservées :**
```python
import ipaddress

# Valider que l'IP n'est pas privée/locale
ip = ipaddress.ip_address(hostname)
if ip.is_private or ip.is_loopback or ip.is_link_local:
    return 'Accès refusé', 403
```

**Règle 2 — Résoudre les domaines et vérifier :**
```python
# Si c'est un hostname, résoudre et vérifier l'IP
resolved_ip = socket.gethostbyname(hostname)
ip = ipaddress.ip_address(resolved_ip)
if ip.is_private:
    return 'Accès refusé : domaine privé', 403
```

**Règle 3 — Utiliser une whitelist (plus sûr) :**
```python
ALLOWED_DOMAINS = ['api.example.com', 'data.example.com']
if hostname not in ALLOWED_DOMAINS:
    return 'Domaine non autorisé', 403
```

## Classification

- **OWASP Top 10 :** A10:2021 — Server-Side Request Forgery (SSRF)
- **CWE :** CWE-918 — Server-Side Request Forgery (SSRF)
- **Impact :** Accès aux ressources internes, vol de credentials cloud, reconnaissance réseau

## Ressources

- [OWASP SSRF](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
- [Capital One 2019 Breach](https://blog.cloudflare.com/capital-one-breach/) — SSRF → AWS metadata → 106 million records
- [PortSwigger SSRF](https://portswigger.net/web-security/ssrf)
