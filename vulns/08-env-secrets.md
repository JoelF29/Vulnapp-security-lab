# Faille 08 — Secrets dans les variables d'environnement mal gérées

## Concept

La faille 07 a corrigé le problème des secrets hardcodés dans le code.
Mais si l'app **affiche les variables d'environnement** sur une page de debug,
un attaquant accède aux secrets directement dans le navigateur.

C'est différent de la faille 07 : les secrets ne sont pas dans le code source,
mais ils sont **exposés par l'application** via une route accessible.

## Code vulnérable

```python
@app.route('/debug')
def debug():
    # FAILLE 08 — affiche TOUTES les vars d'env, y compris AWS_SECRET_ACCESS_KEY
    return render_template('debug.html', env_vars=dict(os.environ))
```

Ou afficher les secrets en clair sur une page de monitoring :
```python
@app.route('/aws')
def aws():
    return render_template('aws.html',
                          access_key=AWS_ACCESS_KEY_ID,      # ← en clair
                          secret_key=AWS_SECRET_ACCESS_KEY)  # ← en clair
```

## Exploit

1. Accéder à `/debug` → voir toutes les variables d'environnement
2. Chercher AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
3. Utiliser `aws configure` avec ces credentials → accès complet à AWS

Ou scanner l'app pour trouver des pages de debug oubliées en production.

## Fix

**Règle 1 — Ne jamais afficher les secrets en clair :**
```python
# Masquer les credentials
return render_template('aws.html',
                      access_key='••••••••••' + AWS_ACCESS_KEY_ID[-4:],
                      secret_key='••••••••••' + AWS_SECRET_ACCESS_KEY[-4:])
```

**Règle 2 — Supprimer les routes de debug en production :**
```python
@app.route('/debug')
def debug():
    # Debug mode seulement si variable d'env explicite
    if not os.getenv('DEBUG_MODE'):
        return redirect(url_for('home'))
    
    # Afficher SEULEMENT les vars non-sensibles
    safe_vars = {k: v for k, v in os.environ.items()
                 if not any(x in k.upper() for x in ['SECRET', 'KEY', 'PASSWORD', 'TOKEN', 'AWS'])}
    return render_template('debug.html', env_vars=safe_vars)
```

**Pourquoi ça corrige :**
- Les secrets ne sont jamais visibles dans le navigateur
- Les routes de debug sont désactivées par défaut
- Si une page affiche des infos, elle filtre les variables sensibles

## Classification

- **OWASP Top 10 :** A02:2021 — Cryptographic Failures
- **CWE :** CWE-532 — Insertion of Sensitive Information into Log File
- **Impact :** Accès aux secrets AWS, compromission de l'infra cloud

## Ressources

- [OWASP Sensitive Data Exposure](https://owasp.org/www-community/Sensitive_Data_Exposure)
- [Secrets Management Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
