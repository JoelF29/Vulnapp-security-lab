# Faille 04 — IDOR (Insecure Direct Object Reference)

## Concept

L'app utilise un identifiant contrôlé par l'utilisateur (l'ID dans l'URL) pour accéder
directement à une ressource en base. Si elle vérifie l'authentification (es-tu connecté ?)
mais pas l'autorisation (as-tu le droit ?), n'importe quel utilisateur peut accéder
aux données de n'importe qui en changeant le chiffre dans l'URL.

## Code vulnérable

```python
@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:          # authentification ✓
        return redirect(url_for('login'))
    # ← pas de vérification d'autorisation
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return render_template('profile.html', user=user)
```

## Exploit

Connecté en tant qu'alice (user_id=1), changer l'URL :
```
/profile/1  →  /profile/2
```
Accès immédiat au profil de bob (email, bio, données personnelles).
Enumération possible : /profile/1, /profile/2, /profile/3...

## Fix

```python
@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Vérification d'autorisation : l'URL doit correspondre à la session
    if user_id != session['user_id']:
        flash("Accès refusé.", 'danger')
        return redirect(url_for('profile', user_id=session['user_id']))
    ...
```

**Pourquoi ça corrige :** la session est signée côté serveur (fix 02) — elle ne peut pas
être falsifiée. Comparer l'ID de l'URL à l'ID en session garantit que chaque utilisateur
n'accède qu'à sa propre ressource.

## Nuance importante

Les profils publics (LinkedIn, Twitter) sont un IDOR intentionnel et acceptable.
IDOR devient critique sur : factures, messages privés, dossiers médicaux, tokens.
La question clé : *cette ressource doit-elle être accessible à tous ou à son propriétaire uniquement ?*

## Classification

- **OWASP Top 10 :** A01:2021 — Broken Access Control (n°1 du classement)
- **CWE :** CWE-639 — Authorization Bypass Through User-Controlled Key
- **Impact :** Accès non autorisé aux données, énumération, violation de vie privée

## Ressources

- [PortSwigger — IDOR](https://portswigger.net/web-security/access-control/idor)
- [OWASP Access Control Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html)
