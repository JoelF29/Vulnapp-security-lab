# Fix 03 — XSS (Cross-Site Scripting)

## Faille
```html
<!-- ❌ Vulnérable — affiche le contenu HTML/JS tel quel -->
<div>{{ c['content'] | safe }}</div>
```

## Fix
```html
<!-- ✓ Sécurisé — Jinja2 échappe automatiquement -->
<div>{{ c['content'] }}</div>
```

**Explication :**
- Retirer le filtre `| safe`
- Jinja2 échappe par défaut : `<script>` → `&lt;script&gt;`
- Le code n'est jamais exécuté, juste affiché comme du texte

## Code complet (app.py)

```python
@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        user_id = session.get('user_id')
        content = request.form['content']

        # ✓ Pas de sanitization — Jinja2 fait le boulot
        # Juste stocker le contenu brut
        db.execute('INSERT INTO comments (user_id, content) VALUES (?, ?)',
                   (user_id, content))
        db.commit()

    comments = db.execute('SELECT * FROM comments').fetchall()
    # Dans le template, {{ c['content'] }} sera automatiquement échappé
    return render_template('comments.html', comments=comments)
```

## Template (templates/comments.html)

```html
{% extends "base.html" %}
{% block title %}Commentaires{% endblock %}

{% block content %}
<h1>Commentaires</h1>

<form method="POST">
    <textarea name="content" required></textarea>
    <button type="submit">Poster</button>
</form>

<!-- ✓ Sécurisé — pas de | safe -->
{% for c in comments %}
    <div class="comment">
        <strong>{{ c['username'] }}</strong>
        <p>{{ c['content'] }}</p>  <!-- Échappé automatiquement -->
    </div>
{% endfor %}
{% endblock %}
```

## Resources
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Jinja2 Auto-Escaping](https://jinja.palletsprojects.com/en/3.0.x/api/#autoescaping)
