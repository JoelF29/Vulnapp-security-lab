# Fix 04 — IDOR (Insecure Direct Object Reference)

## Faille
```python
# ❌ Vulnérable — pas de vérification d'autorisation
@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:  # ✓ Authentification
        return redirect(url_for('login'))
    # ← ❌ Pas d'autorisation — n'importe qui peut voir n'importe quel profil
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return render_template('profile.html', user=user)
```

## Fix
```python
# ✓ Sécurisé — vérification d'autorisation
@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # ✓ Vérifier que l'utilisateur accède à SON profil seulement
    if user_id != session['user_id']:
        flash('Accès refusé.', 'danger')
        return redirect(url_for('home'))

    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return render_template('profile.html', user=user)
```

## Explication
- **Authentification :** Es-tu connecté ? ✓ (checked)
- **Autorisation :** As-tu le droit d'accéder à CET objet ? ✓ (added)
- Toujours comparer l'ID avec `session['user_id']`

## Ressources
- [OWASP IDOR](https://owasp.org/www-community/attacks/Insecure_Direct_Object_Reference)
