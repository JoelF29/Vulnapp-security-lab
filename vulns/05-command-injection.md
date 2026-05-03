# Faille 05 — Command Injection

## Concept

L'app exécute une commande système en y collant directement l'input utilisateur.
Un attaquant peut enchaîner ses propres commandes avec des opérateurs shell
(`&` sur Windows, `;` ou `&&` sur Linux) et les exécuter sur le serveur.
Contrairement à SQLi (accès à la base), Command Injection donne accès à l'OS entier.

## Code vulnérable

```python
host = request.form['host']
result = subprocess.run(
    f"ping -n 1 {host}",   # f-string + shell=True = injection possible
    shell=True, capture_output=True, text=True
).stdout
```

## Exploit

Payload dans le champ ping :
```
8.8.8.8 & whoami
```

Commande exécutée sur le serveur :
```
ping -n 1 8.8.8.8 & whoami
```

Le serveur ping Google **et** exécute `whoami`, les deux résultats s'affichent.

Autres payloads :
```
8.8.8.8 & dir C:\          → liste les fichiers du serveur
8.8.8.8 & type C:\secret   → lit un fichier
8.8.8.8 & net user hacker Password1 /add  → crée un utilisateur admin
```

## Fix

```python
host = request.form['host']
result = subprocess.run(
    ["ping", "-n", "1", host],  # liste d'arguments + shell=False
    shell=False, capture_output=True, text=True
).stdout
```

**Pourquoi ça corrige :**
`shell=False` + liste d'arguments → Python appelle `ping.exe` directement
sans passer par `cmd.exe`. L'opérateur `&` n'est jamais interprété —
il est transmis comme texte brut à ping, qui échoue à résoudre le hostname.

## Classification

- **OWASP Top 10 :** A03:2021 — Injection
- **CWE :** CWE-78 — Improper Neutralization of Special Elements in OS Commands
- **Impact :** Exécution de code arbitraire, compromission totale du serveur

## Ressources

- [PortSwigger — OS Command Injection](https://portswigger.net/web-security/os-command-injection)
- [OWASP Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
