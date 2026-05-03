# Faille 06 — Upload non filtré (Unrestricted File Upload)

## Concept

L'app accepte des fichiers sans vérifier leur extension ni nettoyer leur nom.
Un attaquant peut uploader un script malveillant (web shell) et, s'il trouve
un moyen de l'exécuter, prendre le contrôle du serveur.
Le nom de fichier non nettoyé permet en plus le path traversal : nommer un fichier
`../../../app.py` pour écraser des fichiers en dehors du dossier uploads.

## Code vulnérable

```python
file = request.files.get('file')
filepath = os.path.join('uploads', file.filename)  # nom brut, pas de filtre
file.save(filepath)
```

## Exploit

**Test 1 — extension non filtrée :**
Uploader un fichier `shell.py` → accepté sans restriction.
Sur Linux, l'attaquant peut ensuite chercher à l'exécuter via une autre faille.

**Test 2 — path traversal (Linux) :**
Nommer un fichier `../app.py` et l'uploader → écrase `app.py` à la racine du projet.
*(Bloqué sur Windows par le système de fichiers, fonctionne en prod Linux)*

## Fix

```python
from werkzeug.utils import secure_filename

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt'}
ext = file.filename.rsplit('.', 1)[-1].lower()

if ext not in ALLOWED:
    message = "Extension refusée."
else:
    filename = secure_filename(file.filename)  # retire ../ et caractères dangereux
    file.save(os.path.join('uploads', filename))
```

**Pourquoi ça corrige :**
- Whitelist : tout ce qui n'est pas explicitement autorisé est bloqué
- `secure_filename()` : `../../../app.py` → `app.py`, toujours dans uploads/

## Classification

- **OWASP Top 10 :** A04:2021 — Insecure Design / A05:2021 — Security Misconfiguration
- **CWE :** CWE-434 — Unrestricted Upload of File with Dangerous Type
- **Impact :** Exécution de code (web shell), path traversal, écrasement de fichiers

## Ressources

- [PortSwigger — File Upload Vulnerabilities](https://portswigger.net/web-security/file-upload)
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
