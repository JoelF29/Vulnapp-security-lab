# Fix 06 — File Upload Vulnerability

## Faille
```python
# ❌ Vulnérable — pas de validation du fichier uploadé
from werkzeug.utils import secure_filename
import os

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # ← Juste utiliser le nom du fichier tel quel
    file.save(os.path.join('uploads', file.filename))
    return 'Fichier uploadé'
```

**Attaques possibles :**
1. Upload `.php` ou `.sh` → exécution de code
2. Upload `../../etc/passwd` → path traversal
3. Upload en masse → DoS

## Fix
```python
# ✓ Sécurisé — validation stricte
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    # ✓ Vérifier l'extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    # ✓ Vérifier qu'il y a un fichier
    if not file or file.filename == '':
        return 'Pas de fichier sélectionné', 400

    # ✓ Vérifier l'extension
    if not allowed_file(file.filename):
        return 'Type de fichier non autorisé', 400

    # ✓ Nettoyer le nom du fichier (path traversal)
    filename = secure_filename(file.filename)

    # ✓ Générer un nom unique (éviter les collisions)
    import uuid
    filename = f"{uuid.uuid4()}_{filename}"

    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return 'Fichier uploadé avec succès'
```

## Explication
1. **Whitelist d'extensions :** Seulement PNG, JPG, GIF
2. **secure_filename() :** Nettoie les chemins dangereux
3. **UUID pour le nom :** Évite les collisions et les path traversals
4. **Vérification du contenu :** (bonus) Vérifier le MIME type

## Ressources
- [OWASP File Upload](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
- [werkzeug secure_filename](https://werkzeug.palletsprojects.com/en/2.3.x/utils/#werkzeug.utils.secure_filename)
